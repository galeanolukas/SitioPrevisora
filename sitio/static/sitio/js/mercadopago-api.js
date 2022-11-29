import com.mercadopago.MercadoPago; 
//MercadoPago.SDK.setAccessToken("TEST-7867507306076979-091418-7e221cf9b9d21514d56b55c7143e0ecd-33669542");

//TEST-d989b44c-b8fd-400e-81fb-39e10794b25b
// Crea un objeto de preferencia
MercadoPago.SDK.setAccessToken("TEST-8751409356509512-091421-e076d5ce997fbfcbbd476dfe0adb2b08-645054691");
//...
String token = request.getParameter("token");
String payment_method_id = request.getParameter("payment_method_id");
Int installments = request.getParameter("installments");
Int issuer_id = request.getParameter("issuer_id");

Payment payment = new Payment();
payment.setTransactionAmount(128f)
       .setToken(token)
       .setDescription("Pago cuota Mensual de Afiliado")
       .setInstallments(installments)
       .setPaymentMethodId(payment_method_id)
       .setIssuerId(issuer_id)
       .setPayer(new Payer()
         .setEmail("galeanolukas@gmail.com"));
// Guarda y postea el pago
payment.save();
//...
// Imprime el estado del pago
System.out.println(payment.getStatus());
//...

