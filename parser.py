from owlready2 import *
from cache_store import HistoryManager


class ItsCustomExceptions(Exception):

    def __init__(self, message='Failed to fetch info'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        print('inside custom Exception :::')
        return self.message


class OwlCustomParser:
    def __init__(self):
        print('--OwlCustomParser init--')
        file_ = 'knowledge_base.owl'
        self.ontology = get_ontology(f'{file_}').load()
        self.base_file = file_
        self.base_uri = self.ontology.base_iri
        self.annotation_prop = self.base_uri + "nodeInfo"
        self.app_store = HistoryManager.bind_cache()

    def setting_up_cache(self):
        if HistoryManager.get_store_cache(self.app_store):
            HistoryManager.clear_cache(self.app_store)
        else:
            HistoryManager.store_cache(self.app_store)

    def check_node_type(fun_):
        def inner_fun(self, node):
            concept = [x.name for x in self.ontology.classes()]
            named_individuals = [x.name for x in self.ontology.individuals()]
            each = {'uri': node}
            if node in concept:
                each.update({'type': 'concept',
                             'imp_instance': 'IMP_'+each['uri']})
            elif node in named_individuals:
                each.update({'type': 'individual'})
            else:
                each.update({'type': 'data_property'})
            return fun_(self, each)
        return inner_fun

    @check_node_type
    def construct_query(self, node):

        try:
            history = HistoryManager.get_store_cache(self.app_store)
            if not history:
                raise ItsCustomExceptions('Failed to fetch cache')
            if node.get('type') == 'concept':
                imp_node = f"{self.base_uri}{node['imp_instance']}"
                node_name = f"{self.base_uri}{node['uri']}"

                print(node_name)
                query = "SELECT ?sub_nodes ?nodeInfo  " \
                        + "WHERE { <"+node_name+"> a owl:Class ."\
                        + "?sub_nodes a owl:NamedIndividual ." \
                        + "?sub_nodes rdf:type <"+node_name+">"\
                        + "?sub_nodes <" + self.annotation_prop + "> ?nodeInfo}"
                concept_info = default_world.sparql(query)
                concept_info = [{'uri': x[0].name, 'name':x[1]} for x in concept_info]
                print(list(concept_info))


        except Exception as e:
            message = e
            print(f"Exception caught {e} -- {message}")
            return False,message


if __name__ == '__main__':
    s = OwlCustomParser()
    s.setting_up_cache()
    s.construct_query("Geometry")
