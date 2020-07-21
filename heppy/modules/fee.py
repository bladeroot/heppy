from ..Module import Module
from ..TagData import TagData


class fee(Module):
    opmap = {
        'chkData':      'descend',
    }

    def __init__(self, xmlns):
        Module.__init__(self, xmlns)
        self.name = 'fee'

### RESPONSE parsing

    def parse_cd_tag(self, response, tag):
        feedata = {}
        for child in tag :
            tagname = child.tag.replace('{' + self.xmlns + '}', '')
            feedata.update({tagname: child.text.lower()})

        response.put_to_dict('fee', {
            feedata['name']: feedata
        })

    def parse_cd(self, response, tag):
        return self.parse_cd_tag(response, tag)

    def parse_infData(self, response, tag):
        response.put_extension_block(response, 'fee:info', tag, {
            'currency': [],
            'fee':      [],
            'action':   ['phase', 'subphase'],
            'period':   ['unit'],
        })

    def parse_delData(self, response, tag):
        response.put_extension_block(response, 'fee:delete', tag, {
            'currency': [],
            'credit':   [],
        })

    def parse_trnData(self, response, tag):
        self.parse_typical_tag(response, tag, 'fee:transfer')

    def parse_creData(self, response, tag):
        self.parse_typical_tag(response, tag, 'fee:create')

    def parse_renData(self, response, tag):
        self.parse_typical_tag(response, tag, 'fee:renew')

    def parse_updData(self, response, tag):
        self.parse_typical_tag(response, tag, 'fee:update')

    def parse_typical_tag(self, response, tag, command):
        response.put_extension_block(response, command, tag, {
            'currency': [],
            'fee':      [],
        })

### REQUEST rendering

    def render_check(self, request, data):
        ext = self.render_extension(request, 'check')
        domain = request.add_subtag(ext, 'fee:domain')
        request.add_subtag(domain, 'fee:name',      {}, data.get('name'))
        request.add_subtag(domain, 'fee:currency',  {}, data.get('currency'))
        request.add_subtag(domain, 'fee:command',   {}, data.get('action'))
        request.add_subtag(domain, 'fee:period',    {'unit':'y'}, data.get('period'))

    def render_info(self, request, data):
        self.render_extension_with_fields(request, 'info', [
            TagData('currency', data.get('currency')),
            TagData('action', data.get('action', 'create'), {
                'phase': data.get('phase'),
                'subphase': data.get('subphase'),
            }),
            TagData('period', data.get('period'), {
               'unit': data.get('unit', 'y')
            }),
        ])

    def render_create(self, request, data):
        self.render_extension_with_fields(request, 'create', [
            TagData('currency', data.get('currency')),
            TagData('fee', data.get('fee'))
        ])

    def render_renew(self, request, data):
        self.render_extension_with_fields(request, 'renew', [
            TagData('currency', data.get('currency')),
            TagData('fee', data.get('fee')),
        ])

    def render_transfer(self, request, data):
        self.render_extension_with_fields(request, 'transfer', [
            TagData('currency', data.get('currency')),
            TagData('fee', data.get('fee')),
        ])


