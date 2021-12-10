from owlready2 import *
from cache_store import HistoryManager


class ItsCustomExceptions(Exception):

    def __init__(self, message='Failed to fetch info'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        print('inside custom Exception :::')
        return self.message


def construct_html_data(data, node_type, element_type ='button'):
    str_ = ["<p>See also ↘️</p>️"] if node_type == 'feature' else ["<p>Concepts in geometry</p><br>"]
    class_name = "topic-button" if node_type == 'topic' else "feature-button"
    for element in data:
        if element_type == 'button':
            f = f"<button class =\"{class_name}\" onclick=\"parseInfo(\'{element['uri']}\')\" >" \
                f" {element['nodeInfo']}\
            </button><br>"
            str_.append(f)
    return ''.join(str_)


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

    def initiate_chat(self):
        try:
            root_instance = f"{self.base_uri}{'IMP_Geometry'}"
            root_concept = f"{self.base_uri}{'IMP_Geometry'}"
            prop_name = f"{self.base_uri}is_defined_as"
            # fetch is_defined_as prop value
            query = "SELECT ?value  " \
                    + "WHERE { <" + root_instance + "> a owl:NamedIndividual ." \
                    + "<"+prop_name+"> a owl:DatatypeProperty ." \
                    + " <" + root_instance + ">  <"+prop_name+"> ?value}"
            value = default_world.sparql(query)
            value = [x[0] for x in value][0]
            # fetch sub_nodes
            #Todo
            # fetch general properties
            feature_query = "SELECT ?uri ?nodeInfo "\
                            + "WHERE { <" + root_instance + "> a owl:NamedIndividual ."\
                            + " ?uri a owl:DatatypeProperty ."\
                            + " <" + root_instance + ">  ?uri ?value ." \
                            + "?uri <" + self.annotation_prop + "> ?nodeInfo}"

            data = default_world.sparql(feature_query)
            data = [{'uri': x[0].name,'nodeInfo':x[1]} for x in data]
            print(data)
            value = value + construct_html_data(data, 'feature')
            return {'status': True, 'message': "Please note down...📝", 'data': value}
        except Exception as e:
            print(e)
            return {'message': 'Failed to fetch data', "status": False}

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

