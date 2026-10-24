# مرجع المعمارية التخصصية

مرجع تنفيذي؛ نطاق الدعم العام وكتالوج الأدوات في الدليل الإنجليزي.

```
[Domain Email Operator]
      │
      ├─► [Baseline]   check-email-dns + قراءة القواعد والوجهات
      ├─► [Inbound]    Cloudflare Email Routing: وجهة Verified ← قاعدة لكل عنوان
      ├─► [Outbound]   مزوّد SMTP مجاني ← دومين موثّق يدوياً (TXT/CNAME/DMARC، DNS only) ← Gmail Send mail as
      ├─► [Owner]      حساب، عنوان بريدي، أكواد، مفتاح SMTP، نافذة Gmail
      └─► [Verify]     check-email-dns + سجل المزوّد + رؤوس رسالة تجريبية (SPF/DKIM/DMARC)
```

**قيود ثابتة:** تكلفة صفر، SPF واحد فقط، لا أسرار في الشات، لا عنوان وهمي.
