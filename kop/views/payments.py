# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView

from kop.decorators import superadmin_required, branch_admin_or_superadmin_required
from kop.models import Payment, Invoice
from kop.forms.payment import PaymentForm
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
class CreatePaymentView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        invoice_id = self.kwargs.get('invoice_id')
        self.invoice = get_object_or_404(Invoice, id=invoice_id)
        kwargs['invoice'] = self.invoice
        return kwargs

    def form_valid(self, form):
        invoice_id = self.kwargs.get('invoice_id')
        invoice = get_object_or_404(Invoice, id=invoice_id)

        payment = form.save(commit=False)
        payment.invoice = invoice

        # Generate reference if not provided
        if not payment.reference:
            payment.reference = f"PAY-{invoice.id}-{Payment.objects.count() + 1}"

        payment.save()

        messages.success(
            self.request,
            f"Payment of ${payment.amount} with ${payment.discount_amount} discount applied successfully!"
        )

        return redirect('invoice-detail', pk=invoice.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = self.kwargs.get('invoice_id')
        context['invoice'] = get_object_or_404(Invoice, id=invoice_id)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = invoice.payments.all()

    context = {
        'invoice': invoice,
        'payments': payments,
    }
    return render(request, 'payments/invoice_detail.html', context)
