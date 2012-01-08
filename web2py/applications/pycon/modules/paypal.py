from gluon.html import FORM, INPUT

class PayPal(object):
    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings', None)
	self.request = kwargs.pop('request')
        self.items = dict((
            ('business', self.settings.paypal_business_email),
            ('notify_url', 'http://' + self.request.env.http_host + '/d/ipn'),
            ('cmd', '_cart'),
            ('upload', '1'),
            ('charset', 'utf-8'),
            ('no_note', '1'),
            ('no_shipping', '1'),
            ('cancel_return', 'http://' + self.request.env.http_host + '/d/payment_processed/cancel'),
            ('return', 'http://' + self.request.env.http_host + '/d/payment_processed/paypal'),
            ('currency_code', 'SGD')))
        self.items.update(**kwargs)
    
    def form(self):
        return FORM(INPUT(_type='submit', _value='PayPal'),
            *[INPUT(_name=i[0], _type="hidden", _value=i[1]) for i in self.items.iteritems()],
            _action=self.settings.paypal_url,
            _enctype='',
            _method='POST')
    
    def encrypted_form(self):
        return FORM(INPUT(_type='submit', _name="submit", _value='PayPal'),
            INPUT(_type='hidden', _name='cmd', _value='_s-xclick'),
            INPUT(_type='hidden', _name='encrypted', _value=self._encrypt()),
            _action=self.settings.paypal_url,
            _enctype='',
            _method='POST')

    def _encrypt(self):
        """Use your key thing to encrypt things."""
        from M2Crypto import BIO, SMIME, X509
        CERT = self.settings.private_cert
        PUB_CERT = self.settings.public_cert
        PAYPAL_CERT = self.settings.paypal_cert
        CERT_ID = self.settings.cert_id

        # Iterate through the fields and pull out the ones that have a value.
        plaintext = 'cert_id=%s' % CERT_ID
        for name, value in self.items.iteritems():
            plaintext += '\n%s=%s' % (name, value)
        #plaintext = plaintext.encode('utf-8')

        # Begin crypto weirdness.
        s = SMIME.SMIME()    
        s.load_key_bio(BIO.openfile(CERT), BIO.openfile(PUB_CERT))
        p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)
        x509 = X509.load_cert_bio(BIO.openfile(PAYPAL_CERT))
        sk = X509.X509_Stack()
        sk.push(x509)
        s.set_x509_stack(sk)
        s.set_cipher(SMIME.Cipher('des_ede3_cbc'))
        tmp = BIO.MemoryBuffer()
        p7.write_der(tmp)
        p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)
        out = BIO.MemoryBuffer()
        p7.write(out)
        return out.read()
