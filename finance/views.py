from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from students.models import Student
from .forms import FeeStructureForm, StudentFeeForm, ExtraFeeForm, FeeInstallmentForm, PromoteStudentFeeForm
from .models import FeeStructure, StudentFee, ExtraFee, FeeInstallment


@login_required
def fee_structure_list(request):
    items = FeeStructure.objects.select_related('department', 'course').all()
    return render(request, 'finance/fee_structure_list.html', {'items': items})


@login_required
def fee_structure_add(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure added successfully.")
            return redirect('fee_structure_list')
    else:
        form = FeeStructureForm()
    return render(request, 'finance/fee_structure_form.html', {'form': form})


@login_required
def fee_structure_edit(request, pk):
    item = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure updated successfully.")
            return redirect('fee_structure_list')
    else:
        form = FeeStructureForm(instance=item)
    return render(request, 'finance/fee_structure_form.html', {'form': form, 'is_edit': True})


@login_required
def student_fee_list(request):
    q = request.GET.get('q', '')
    items = StudentFee.objects.select_related('student', 'fee_structure').all()

    if q:
        items = items.filter(
            Q(student__name__icontains=q) |
            Q(student__enrollment_number__icontains=q) |
            Q(academic_year__icontains=q)
        )

    return render(request, 'finance/student_fee_list.html', {
        'items': items,
        'q': q
    })


@login_required
def student_fee_add(request):
    if request.method == 'POST':
        form = StudentFeeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            if obj.fee_structure and not obj.base_amount:
                obj.base_amount = obj.fee_structure.total_amount

            obj.save()
            messages.success(request, "Student fee fixed successfully.")
            return redirect('student_fee_list')
    else:
        form = StudentFeeForm()
    return render(request, 'finance/student_fee_form.html', {'form': form})


@login_required
def student_fee_detail(request, pk):
    item = get_object_or_404(
        StudentFee.objects.select_related('student', 'fee_structure'),
        pk=pk
    )
    extras = item.extra_fees.all()
    installments = item.installments.all()

    return render(request, 'finance/student_fee_detail.html', {
        'item': item,
        'extras': extras,
        'installments': installments
    })


@login_required
def extra_fee_add(request, pk):
    student_fee = get_object_or_404(StudentFee, pk=pk)

    if request.method == 'POST':
        form = ExtraFeeForm(request.POST)
        if form.is_valid():
            extra = form.save(commit=False)
            extra.student_fee = student_fee
            extra.save()
            messages.success(request, "Extra fee added successfully.")
            return redirect('student_fee_detail', pk=student_fee.id)
    else:
        form = ExtraFeeForm()

    return render(request, 'finance/extra_fee_form.html', {
        'form': form,
        'student_fee': student_fee
    })


@login_required
def installment_add(request, pk):
    student_fee = get_object_or_404(StudentFee, pk=pk)

    if request.method == 'POST':
        form = FeeInstallmentForm(request.POST, student_fee=student_fee)
        if form.is_valid():
            installment = form.save(commit=False)
            installment.student_fee = student_fee
            installment.save()
            messages.success(request, "Installment added successfully.")
            return redirect('student_fee_detail', pk=student_fee.id)
    else:
        form = FeeInstallmentForm(student_fee=student_fee)

    return render(request, 'finance/installment_form.html', {
        'form': form,
        'student_fee': student_fee
    })


@login_required
def installment_edit(request, pk):
    installment = get_object_or_404(FeeInstallment, pk=pk)
    student_fee = installment.student_fee

    if request.method == 'POST':
        form = FeeInstallmentForm(request.POST, instance=installment, student_fee=student_fee)
        if form.is_valid():
            form.save()
            messages.success(request, "Installment updated successfully.")
            return redirect('student_fee_detail', pk=student_fee.id)
    else:
        form = FeeInstallmentForm(instance=installment, student_fee=student_fee)

    return render(request, 'finance/installment_form.html', {
        'form': form,
        'student_fee': student_fee,
        'is_edit': True
    })


@login_required
def installment_delete(request, pk):
    installment = get_object_or_404(FeeInstallment, pk=pk)
    student_fee = installment.student_fee

    if request.method == 'POST':
        installment.delete()
        messages.success(request, "Installment deleted successfully.")
        return redirect('student_fee_detail', pk=student_fee.id)

    return render(request, 'finance/installment_delete.html', {
        'installment': installment
    })


@login_required
def installment_receipt_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    installment = get_object_or_404(
        FeeInstallment.objects.select_related('student_fee', 'student_fee__student'),
        pk=pk
    )

    student_fee = installment.student_fee
    student = student_fee.student

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{installment.receipt_no}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    _, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, y, "College ERP Fee Receipt")

    y -= 35
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Receipt No: {installment.receipt_no}")
    y -= 20
    p.drawString(50, y, f"Student Name: {student.name}")
    y -= 20
    p.drawString(50, y, f"Enrollment No: {student.enrollment_number}")
    y -= 20
    p.drawString(50, y, f"Academic Year: {student_fee.academic_year}")
    y -= 20
    p.drawString(50, y, f"Year: {student_fee.year}")
    y -= 20
    p.drawString(50, y, f"Semester: {student_fee.semester if student_fee.semester else '-'}")
    y -= 20
    p.drawString(50, y, f"Amount Paid: {installment.amount_paid}")
    y -= 20
    p.drawString(50, y, f"Payment Date: {installment.payment_date}")
    y -= 20
    p.drawString(50, y, f"Payment Mode: {installment.payment_mode}")
    y -= 20
    p.drawString(50, y, f"Reference No: {installment.reference_no or '-'}")
    y -= 20
    p.drawString(50, y, f"Received By: {installment.received_by or '-'}")
    y -= 20
    p.drawString(50, y, f"Remaining Pending: {student_fee.pending_amount}")
    y -= 30
    p.drawString(50, y, "This is a computer generated receipt.")

    p.save()
    return response


@login_required
def promote_student_fee(request):
    if request.method == 'POST':
        form = PromoteStudentFeeForm(request.POST)
        if form.is_valid():
            current_fee = form.cleaned_data['current_student_fee']
            next_academic_year = form.cleaned_data['next_academic_year']
            next_year = form.cleaned_data['next_year']
            next_semester = form.cleaned_data['next_semester']

            student = current_fee.student

            if StudentFee.objects.filter(
                student=student,
                academic_year=next_academic_year,
                year=next_year,
                semester=next_semester
            ).exists():
                messages.error(request, "Next year fee record already exists.")
                return redirect('student_fee_list')

            fee_structure = FeeStructure.objects.filter(
                course=student.course_fk,
                academic_year=next_academic_year,
                year=next_year,
                semester=next_semester,
                is_active=True
            ).first()

            base_amount = fee_structure.total_amount if fee_structure else 0

            StudentFee.objects.create(
                student=student,
                fee_structure=fee_structure,
                academic_year=next_academic_year,
                year=next_year,
                semester=next_semester,
                base_amount=base_amount,
                notes=f"Promoted from {current_fee.academic_year}",
                is_locked=True
            )

            messages.success(request, "Next year fee generated successfully.")
            return redirect('student_fee_list')
    else:
        form = PromoteStudentFeeForm()

    return render(request, 'finance/promote_student_fee.html', {'form': form})


@login_required
def my_fees(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    items = StudentFee.objects.filter(student=student).order_by('-academic_year', '-year', '-semester')

    return render(request, 'finance/my_fees.html', {
        'items': items,
        'student': student
    })


from django.shortcuts import redirect


def finance_home(request):
    if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
        return redirect("student_fee_list")
    elif getattr(request.user, "role", None) == "student":
        return redirect("my_fees")
    return redirect("fee_structure_list")