from copy import deepcopy

from dts_api.funcs.common import set_dts_resource


class DtsResource:

    def __init__(self, namespace, nsmap):

        self.dts_resource = set_dts_resource()
        self.nsmap = nsmap
        self.namespace = namespace

    def set_dts_resource(self, *args, **kwargs):

        resource, namespace, nsmap, document, cite_structure, toc = args
        if kwargs:
            _, = kwargs

        document_copy = deepcopy(document.getroot())

        for pi in document.xpath('//processing-instruction()'):
            self.dts_resource.find('%sproc' % namespace, namespaces=nsmap).append(deepcopy(pi))
        self.dts_resource.find('%sDocument' % namespace, namespaces=nsmap).set('resource', resource)
        self.dts_resource.find('%sDocument' % namespace, namespaces=nsmap).append(document_copy)
        self.dts_resource.find('%sCitationTrees' % namespace, namespaces=nsmap).extend(deepcopy(cite_structure))
        self.dts_resource.find('%sTableOfContent' % namespace).append(deepcopy(toc.getroot()))

        return self.dts_resource