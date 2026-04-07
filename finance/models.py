from django.db import models
from django.utils import timezone
from students.models import Student
from departments.models import Department
from courses.models import Course


class FeeStructure(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    academic_year = models.CharField(max_length=20)   # Example: 2025-26
    year = models.PositiveSmallIntegerField()         # 1,2,3,4
    semester = models.PositiveSmallIntegerField(null=True, blank=True)

    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-academic_year', 'course']
        unique_together = ('course', 'academic_year', 'year', 'semester')

    def __str__(self):
        sem = f"Sem {self.semester}" if self.semester else "All Sem"
        return f"{self.course} | {self.academic_year} | Year {self.year} | {sem}"

    @property
    def total_amount(self):
        return (
            self.admission_fee +
            self.tuition_fee +
            self.exam_fee +
            self.library_fee +
            self.lab_fee +
            self.other_fee
        )


class StudentFee(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_fees'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    academic_year = models.CharField(max_length=20)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField(null=True, blank=True)

    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(default=True)  # once admission fee fixed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-academic_year', 'student__name']
        unique_together = ('student', 'academic_year', 'year', 'semester')

    def __str__(self):
        sem = f"Sem {self.semester}" if self.semester else "All Sem"
        return f"{self.student.name} | {self.academic_year} | Year {self.year} | {sem}"

    @property
    def extra_total(self):
        total = self.extra_fees.aggregate(total=models.Sum('amount'))['total']
        return total or 0

    @property
    def total_payable(self):
        return self.base_amount + self.extra_total

    @property
    def total_paid(self):
        total = self.installments.aggregate(total=models.Sum('amount_paid'))['total']
        return total or 0

    @property
    def pending_amount(self):
        return self.total_payable - self.total_paid


class ExtraFee(models.Model):
    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='extra_fees'
    )
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True, null=True)
    added_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-added_on', '-id']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class FeeInstallment(models.Model):
    PAYMENT_MODE_CHOICES = (
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
    )

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    receipt_no = models.CharField(max_length=30, unique=True, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, default='Cash')
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    received_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['-payment_date', '-id']

    def __str__(self):
        return f"{self.student_fee.student.name} - {self.amount_paid} - {self.payment_date}"

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            last_id = FeeInstallment.objects.count() + 1
            self.receipt_no = f"RCPT-{timezone.now().year}-{last_id:05d}"
        super().save(*args, **kwargs)

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, default='Cash')
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    received_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['-payment_date', '-id']

    def __str__(self):
        return f"{self.student_fee.student.name} - {self.amount_paid} - {self.payment_date}"