from owlready2 import *
from cache_store import HistoryManager


class ItsCustomExceptions(Exception):

    def __init__(self, message='Failed to fetch info'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        print('inside custom Exception :::')
        return self.message


def construct_html_data(data, node_type, pre_msg, element_type ='button'):
    if not data:
        return ''
    str_ = [pre_msg]
    class_name = "topic-button" if node_type == 'topic' else "feature-button"
    for element in data:
        if element_type == 'button':
            f = f"<button class =\"{class_name}\" onclick=\"parseInfo(\'{element['uri']}\')\" >" \
                f" {element['nodeInfo']}\
            </button><br>"
            str_.append(f)
    return ''.join(str_)


def build_query(node_data, query_type):
    """
    query_type:
        - data_assertion: <IMP_Node> <is_defined_as> <value>
          return:query
        - sub_nodes:<concept><subclass_of><?parent> / individuals(?parent)
          return: query
    """
    if query_type == 'data_assertions':
        root_instance = node_data['property_of']
        prop_name = node_data['property']
        query = "SELECT ?value  " \
            + "WHERE { <" + root_instance + "> a owl:NamedIndividual ." \
            + "<" + prop_name + "> a owl:DatatypeProperty ." \
            + " <" + root_instance + ">  <" + prop_name + "> ?value}"
        return query
    if query_type == 'sub_classes':
        annotation_name = node_data['annotation']
        concept = node_data['concept']
        query = "SELECT ?uri ?nodeInfo   " \
            + "WHERE { <" + concept + "> a owl:Class ." \
            + "?uri rdfs:subClassOf <" + concept + "> ." \
            + "?uri <" + annotation_name + "> ?nodeInfo}"
        return query

    if query_type == 'instances':
        annotation_name = node_data['annotation']
        concept = node_data['concept']
        print("---- IS ---"+concept)
        query = "SELECT ?uri ?nodeInfo   " \
                + "WHERE { <" + concept + "> a owl:Class ." \
                + "?uri a owl:NamedIndividual ."\
                + "?uri rdf:type <" + concept + "> " \
                + "?uri <" + annotation_name + "> ?nodeInfo }"

        return query

    if query_type == 'properties':
        annotation_name = node_data['annotation']
        root_instance = node_data['property_of']
        query = "SELECT ?uri ?nodeInfo " \
            + "WHERE { <" + root_instance + "> a owl:NamedIndividual ." \
            + " ?uri a owl:DatatypeProperty ." \
            + " <" + root_instance + ">  ?uri ?value ." \
            + "?uri <" + annotation_name + "> ?nodeInfo}"
        return query
    if query_type == 'domain':
        prop_name = node_data['property']
        query = "SELECT ?uri " \
                + "WHERE { <" + prop_name + "> a owl:DatatypeProperty ." \
                + " <" + prop_name + ">  rdfs:domain ?uri .}"
        return query

    if query_type == 'data_property_axiom':
        prop_name = node_data['property']
        annotation_name = node_data['annotation']
        query = "SELECT ?uri ?nodeInfo " \
                + "WHERE { <" + prop_name + "> a owl:DatatypeProperty ." \
                + "?uri a owl:NamedIndividual ."\
                + "?uri <"+prop_name+"> ?value ."\
                + "?uri <" + annotation_name + "> ?nodeInfo}"
        print(query)
        return query


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
            root_concept = f"{self.base_uri}{'Geometry'}"
            prop_name = f"{self.base_uri}is_defined_as"
            annotation = self.annotation_prop
            # fetch is_defined_as prop value
            query = build_query({'property_of': root_instance,
                                 'property': prop_name}, 'data_assertions')
            value = default_world.sparql(query)
            value = [x[0] for x in value][0]
            # fetch sub_nodes
            #Todo
            node_query = build_query({'concept': root_concept,
                                      'annotation': annotation}, 'sub_classes')
            sub_nodes = default_world.sparql(node_query)
            sub_nodes = [{'uri': x[0].name, 'nodeInfo':x[1]} for x in sub_nodes]
            # print(sub_nodes)
            value = value + construct_html_data(sub_nodes, 'topic', "<p>Concepts in geometry ↘️</p>")
            # fetch general properties
            feature_query = build_query({'annotation': annotation,
                                         'property_of': root_instance}, 'properties')

            data = default_world.sparql(feature_query)
            data = [{'uri': x[0].name, 'nodeInfo':x[1]} for x in data]
            # print(data)
            value = value + construct_html_data(data, 'feature', "<p>See also ↘️</p>️")
            HistoryManager.store_cache(self.app_store, data={"concept": "Geometry"})
            HistoryManager.display_store(self.app_store)
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
                print('type concept')
                imp_node = f"{self.base_uri}{node['imp_instance']}"
                node_name = f"{self.base_uri}{node['uri']}"
                prop_name = f"{self.base_uri}is_defined_as"
                value_query = build_query({'property_of': imp_node,
                                     'property': prop_name}, 'data_assertions')
                value = default_world.sparql(value_query)
                value = [x[0] for x in value][0]
                sub_node_query = build_query({'concept': node_name,
                                              'annotation': self.annotation_prop}, 'sub_classes')
                concept_info = default_world.sparql(sub_node_query)
                concept_info = [{'uri': x[0].name, 'nodeInfo':x[1]} for x in concept_info]
                if not concept_info:
                    print('not concept info')
                    instance_query = build_query({'concept': node_name,
                                              'annotation': self.annotation_prop}, 'instances')
                    print('not concept info 2')
                    print(instance_query)
                    concept_info = default_world.sparql(instance_query)
                    print("Here e got ---????")
                    print(list(concept_info))
                    concept_info = [{'uri': x[0].name, 'nodeInfo':x[1]} for x in concept_info if x[0].name != node['imp_instance']]
                    #todo fetch Named Individls
                value = value + construct_html_data(concept_info, 'topic',"<p>Concepts in geometry ↘️</p>")
                HistoryManager.store_specfic(self.app_store, 'concept', node['uri'])
                HistoryManager.display_store(self.app_store)
                return {'status': True, 'message': "Please note down...📝", 'data': value}

            if node.get('type') == 'individual':
                node_name = f"{self.base_uri}{node['uri']}"
                annotation_prop = self.annotation_prop
                previous_prop = HistoryManager.get_store_cache(self.app_store, key="property")
                prop_name = f"{self.base_uri}is_defined_as" if not previous_prop else f"{self.base_uri}{previous_prop}"
                value_query = build_query({'property_of': node_name,
                                           'property': prop_name}, 'data_assertions')
                value = default_world.sparql(value_query)
                value = [x[0] for x in value][0]
                print("issue here ----->>>>")
                if not previous_prop:

                    # fetch general properties
                    feature_query = build_query({'annotation': annotation_prop,
                                                 'property_of': node_name}, 'properties')

                    data = default_world.sparql(feature_query)
                    data = [{'uri': x[0].name, 'nodeInfo': x[1]} for x in data]
                    # print(data)
                    value = value + construct_html_data(data, 'feature', "<p>See also ↘️</p>️")
                    HistoryManager.store_specfic(self.app_store, 'instance', node['uri'])
                    HistoryManager.display_store(self.app_store)
                return {'status': True, 'message': "Please note down...📝", 'data': value}
            if node.get('type') == 'data_property':
                prop_name = f"{self.base_uri}{node['uri']}"
                annotation_prop = self.annotation_prop
                previous_instance = HistoryManager.get_store_cache(self.app_store, key="instance")
                print(f"--- PREVIOUS INSTANCE --- {previous_instance}")
                content = ''
                if not previous_instance:
                    # Fetch all nodes under that
                    domain_query = build_query({'property': prop_name}, 'domain')
                    domain = list(default_world.sparql(domain_query))[0][0].name
                    root_instance_name = f"IMP_{domain}"
                    root_instance = f"{self.base_uri}{root_instance_name}"
                    value_query = build_query({'property_of': root_instance,
                                               'property': prop_name}, 'data_assertions')
                    value = default_world.sparql(value_query)
                    content = '' if not value else [x[0] for x in value][0]
                    print("------ NNNNN----")
                    # query for all individuals under feature
                    ind_query = build_query({'property': prop_name,
                                             'annotation': annotation_prop}, "data_property_axiom")
                    print("here im")
                    inds = default_world.sparql(ind_query)
                    data = [{'uri': x[0].name, 'nodeInfo': x[1]} for x in inds if x[0].name != root_instance_name ]

                    if data:
                        step_text = "<br> Following topics also coverd this feature <br> "
                        content = content + construct_html_data(data, 'topic', step_text)
                else:
                    value_query = build_query({'property_of':  f"{self.base_uri}{previous_instance}",
                                               'property': prop_name}, 'data_assertions')
                    value = default_world.sparql(value_query)
                    content = [x[0] for x in value][0]
                HistoryManager.store_specfic(self.app_store, 'property', node['uri'])
                HistoryManager.display_store(self.app_store)
                return {'status': True, 'message': "Please note down...📝", 'data': content}

        except Exception as e:
            message = e
            print(f"Exception caught {e} -- {message}")
            return False, message


if __name__ == '__main__':
    s = OwlCustomParser()
    s.setting_up_cache()
    s.construct_query("Geometry")

