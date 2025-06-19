from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),  # ingresos
        ('expense', 'Expense'), # gastos
		('transfer', 'Transfer'),  # transferencias
		('investment', 'Investment'),  # inversiones
		('loan', 'Loan'),  # préstamos
		('debt', 'Debt'),  # deudas
		('savings', 'Savings'),  # ahorros
		('other', 'Other'),  # otros
    )

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.type} - {self.amount} - {self.date}"