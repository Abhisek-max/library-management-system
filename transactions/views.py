from datetime import timedelta, datetime
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from accounts.decorators import roles_required
from accounts.models import User
from books.models import Book
from .models import ActivityLog, Loan, Notification, Reservation


def log_action(actor, action, details=""):
    ActivityLog.objects.create(actor=actor, action=action, details=details)


@login_required
def my_loans(request):
    return render(
        request,
        "transactions/my_loans.html",
        {"loans": Loan.objects.filter(student=request.user).select_related("book")},
    )


@login_required
def request_loan(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        if book.available_copies < 1:
            messages.error(request, "This book is currently unavailable.")
        elif Loan.objects.filter(
            student=request.user, book=book, status__in=["PENDING", "ISSUED"]
        ).exists():
            messages.warning(
                request, "You already have an active request for this book."
            )
        else:
            Loan.objects.create(student=request.user, book=book)
            log_action(request.user, "Borrow request", book.title)
            messages.success(request, "Borrow request sent to the library.")
    return redirect("books:detail", pk=pk)


@login_required
def reserve(request, pk):
    if request.method == "POST":
        Reservation.objects.get_or_create(student=request.user, book_id=pk)
        messages.success(request, "Reservation request recorded.")
    return redirect("books:detail", pk=pk)


@login_required
def renew(request, pk):
    loan = get_object_or_404(Loan, pk=pk, student=request.user, status="ISSUED")
    if (
        request.method == "POST"
        and loan.renewals < 2
        and loan.due_date >= timezone.localdate()
    ):
        loan.due_date += timedelta(days=14)
        loan.renewals += 1
        loan.save()
        log_action(request.user, "Loan renewed", loan.book.title)
        messages.success(request, "Loan renewed for 14 days.")
    else:
        messages.error(request, "This loan cannot be renewed.")
    return redirect("transactions:my_loans")


@roles_required("ADMIN", "LIBRARIAN")
def manage(request):
    return render(
        request,
        "transactions/manage.html",
        {"loans": Loan.objects.select_related("student", "book")},
    )


@roles_required("ADMIN", "LIBRARIAN")
@transaction.atomic
def action(request, pk, action):
    loan = get_object_or_404(Loan.objects.select_for_update(), pk=pk)
    if request.method == "POST":
        if (
            action == "approve"
            and loan.status == "PENDING"
            and loan.book.available_copies > 0
        ):
            loan.status = "ISSUED"
            loan.issued_at = timezone.now()
            loan.due_date = timezone.localdate() + timedelta(days=14)
            loan.book.available_copies -= 1
            loan.book.save()
            Notification.objects.create(
                user=loan.student,
                title="Book issued",
                body=f"{loan.book.title} is due on {loan.due_date}.",
            )
            log_action(
                request.user,
                "Book issued",
                f"{loan.book.title} to {loan.student.username}",
            )
        elif action == "reject" and loan.status == "PENDING":
            loan.status = "REJECTED"
            log_action(request.user, "Borrow request rejected", loan.book.title)
        elif action == "return" and loan.status == "ISSUED":
            loan.fine_amount = loan.calculate_fine()
            loan.status = "RETURNED"
            loan.returned_at = timezone.now()
            loan.book.available_copies += 1
            loan.book.save()
            Notification.objects.create(
                user=loan.student,
                title="Book returned",
                body=f"Return completed. Fine: INR {loan.fine_amount}.",
            )
            log_action(request.user, "Book returned", loan.book.title)
        else:
            messages.error(request, "This action is not available.")
            return redirect("transactions:manage")
        loan.save()
        messages.success(request, "Transaction updated.")
    return redirect("transactions:manage")


@roles_required("ADMIN", "LIBRARIAN")
def quick_issue(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        member = request.POST.get("member", "").strip()
        due_date_str = request.POST.get("due_date", "").strip()

        book = Book.objects.filter(isbn=identifier).first()
        user = User.objects.filter(username=member).first()

        if not book or not user:
            messages.error(request, "Enter a valid ISBN/barcode and member username.")

        elif not user.is_approved:
            messages.error(request, "This member is awaiting approval.")

        elif book.available_copies < 1:
            messages.error(request, "This book is unavailable.")

        else:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Please select a valid due date.")
                return redirect("transactions:quick_issue")

            if due_date <= timezone.localdate():
                messages.error(request, "Due date must be later than today.")
                return redirect("transactions:quick_issue")

            loan = Loan.objects.create(
                student=user,
                book=book,
                status="ISSUED",
                issued_at=timezone.now(),
                due_date=due_date,
            )

            book.available_copies -= 1
            book.save()

            Notification.objects.create(
                user=user,
                title="Book issued",
                body=f"{book.title} is due on {loan.due_date}.",
            )

            log_action(
                request.user,
                "Quick issue",
                f"{book.title} to {user.username}",
            )

            messages.success(
                request,
                f"{book.title} issued successfully to {user.username}.",
            )

        return redirect("transactions:quick_issue")

    return render(request, "transactions/quick_issue.html")


@roles_required("ADMIN", "LIBRARIAN")
def members(request):
    users = User.objects.exclude(role="ADMIN").order_by("-date_joined")
    return render(request, "transactions/members.html", {"users": users})


@roles_required("ADMIN", "LIBRARIAN")
def approve_member(request, pk):
    user = get_object_or_404(User, pk=pk, role="FACULTY")
    if request.method == "POST":
        user.is_approved = True
        user.save(update_fields=["is_approved"])
        Notification.objects.create(
            user=user,
            title="Faculty account approved",
            body="Your library account is now active.",
        )
        log_action(request.user, "Faculty approved", user.username)
        messages.success(
            request, f"{user.get_full_name() or user.username} is approved."
        )
    return redirect("transactions:members")


@roles_required("ADMIN", "LIBRARIAN")
def reports(request, format):
    rows = Loan.objects.select_related("student", "book").all()
    if format == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.title = "Library transactions"
        ws.append(
            ["Member", "Book", "Status", "Issued", "Due date", "Returned", "Fine"]
        )
        for x in rows:
            ws.append(
                [
                    x.student.username,
                    x.book.title,
                    x.status,
                    x.issued_at.strftime("%Y-%m-%d") if x.issued_at else "",
                    str(x.due_date or ""),
                    x.returned_at.strftime("%Y-%m-%d") if x.returned_at else "",
                    float(x.fine_amount),
                ]
            )
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=library-report.xlsx"
        wb.save(response)
        return response
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Library Transaction Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 800, "LibraryOS - Transaction Report")
    pdf.setFont("Helvetica", 9)
    y = 775
    for x in rows:
        pdf.drawString(
            40,
            y,
            f'{x.student.username} | {x.book.title[:45]} | {x.status} | Due: {x.due_date or "-"} | Fine: INR {x.fine_amount}',
        )
        y -= 16
        if y < 45:
            pdf.showPage()
            y = 800
            pdf.setFont("Helvetica", 9)
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=library-report.pdf"
    return response


@roles_required("ADMIN", "LIBRARIAN")
def activity_log(request):
    return render(
        request,
        "transactions/activity_log.html",
        {"items": ActivityLog.objects.select_related("actor")[:100]},
    )


@login_required
def notifications(request):
    items = request.user.notifications.all()
    items.update(read=True)
    return render(request, "transactions/notifications.html", {"items": items})
