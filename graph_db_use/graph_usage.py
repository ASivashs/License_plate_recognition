from py2neo import Graph, Node, Relationship, Subgraph
from py2neo.matching import *


class GraphUse:
    def __init__(self):
        self._graph = Graph("neo4j+s://59f72573.databases.neo4j.io",
                            auth=("neo4j", "uqPApwGmqjBvfT-fqUayvf8ETlYMb0i2yFZzHhrNz1k"))  # Initialize DB
        # self._graph = Graph("bolt://localhost:7687",
        #                     auth=("neo4j", "danila02"))  # Initialize DB
        self._data_before_change = self._graph.query("MATCH (n) RETURN (n)").to_ndarray()

    @staticmethod
    def __convert_list(list_ndarray) -> list:
        """
        Convert ndarray list to list with names nodes
        :param list_ndarray: graph converting to ndarray
        :return: list names nodes
        """
        list_el = []
        for node_el in list_ndarray:
            node_el_dict = dict(*node_el)
            for value in node_el_dict:
                list_el.append(node_el_dict[value])
        return list_el

    def __update_data_before_change(self) -> None:
        self._data_before_change = self._graph.query("MATCH (n) RETURN (n)").to_ndarray()

    def __find_vertex_after_change(self) -> str:
        """
        Find new add vertex
        :return: find new Node
        """
        set_before_change = set(self.__convert_list(self._data_before_change))
        set_after_change = set(self.__convert_list(self._graph.query("MATCH (n) RETURN (n)").to_ndarray()))
        inter_sec_set = set_after_change.difference(set_before_change)
        self.__update_data_before_change()
        try:
            return NodeMatcher(self._graph).match(name=inter_sec_set.pop()).first()
        except KeyError:
            print("Не было обнаружено новой вершины")

    def __check_exists_vertex(self, type_: str, add_ver: str) -> bool:  # Может убрать эту функцию
        """
        Same name check
        :param add_ver: Vertex to check
        :param type_: name_photo for class Photo, num_auto for class ExistsNum
        :return: bool
        """
        match type_:
            case "name_photo":
                bool_res = NodeMatcher(self._graph).match(name=add_ver).exists()
            case "num_auto":
                bool_res = NodeMatcher(self._graph).match("ExistsNum", name=add_ver).exists()

        if not bool_res:
            return False
        else:
            print("Вершина с таким названием уже существует")
            return True

    def __analyse_node(self, new_node) -> None:
        if new_node.has_label("Photo"):
            dict_data_photo_ = {
                'NUM_AUTO': 'k275lp',
                'COLOR': 'red',
                'MARK': 'BMW',
            }
            self.__add_photo_with_relation_ver_intersec(dict_data=dict_data_photo_)

    def __add_photo_with_relation_ver_intersec(self, dict_data: dict) -> None:
        """
        Add name_photo with relations
        :param dict_data: dict key can be: name_photo, NUM_AUTO, COLOR, MARK
        :return: None
        """
        list_of_nodes, list_of_relations = [], []
        main_node = self.__find_vertex_after_change()
        try:
            for key, value in dict_data.items():
                nodes = Node("Photo_data", name=value)
                relation = Relationship(main_node, key, nodes)
                list_of_nodes.append(nodes)
                list_of_relations.append(relation)
        except TypeError:
            print('Вершина с названием фото не создана')

        subgraph = Subgraph(nodes=list_of_nodes,
                            relationships=list_of_relations)
        self._graph.create(subgraph)

    def print_all_data(self) -> None:
        print(self._graph.query(
            "MATCH (n)-[rel]->(p)"
            "RETURN n.name as vert_1, type(rel) as relation, p.name as vert_2").to_data_frame())
        print(self._graph.query(
            "MATCH (n)"
            "WHERE NOT (n)-[]->() and not ()-[]->(n)"
            "RETURN n.name as standalone_vert").to_data_frame())

    def add_new_node(self, class_: str, name_picture: str) -> None:
        """
        Add new node in DB
        :param class_: name of class of vertex
        :param name_picture: name of vertex
        :return: None
        """
        if not GraphUse.__check_exists_vertex(self, type_="name_photo", add_ver=name_picture):
            new_node = Node(class_, name=name_picture)
            self._graph.create(new_node)
            self.__analyse_node(new_node)

    def add_num_auto_for_entry(self, num_auto: str, first_name_: str, last_name_: str) -> bool:
        """
        Add new num auto for entry in DB, also first name, last name
        :param num_auto: uniq num auto
        :param first_name_: first name driver
        :param last_name_: last name driver
        :return: None
        """
        if not GraphUse.__check_exists_vertex(self, type_="num_auto", add_ver=num_auto):
            main_node = Node("ExistsNum", name=num_auto)
            first_name_node = Node("Person", name=first_name_)
            last_name_node = Node("Person", name=last_name_)
            rel_main_first = Relationship(main_node, "FIRST_NAME", first_name_node)
            rel_main_last = Relationship(main_node, "LAST_NAME", last_name_node)
            subgraph = Subgraph(nodes=[main_node, first_name_node, last_name_node],
                                relationships=[rel_main_first, rel_main_last])
            self._graph.create(subgraph)
            return True
        else:
            return False

    def delete_num_auto_for_entry(self, num_auto: str):
        if NodeMatcher(self._graph).match("ExistsNum", name=num_auto).exists():
            self._graph.run(f"match (n:ExistsNum)-[]->(p)"
                            f"where n.name = \"{num_auto}\""
                            f"detach delete n, p")
            return True
        else:
            return False

    def add_new_relation(self, class_1: str, name_picture_1: str, class_2: str, name_picture_2: str,
                         relation: str) -> None:
        """
        Creating a new relationship between two existing nodes
        :returns: None
        """
        try:
            nodes = NodeMatcher(self._graph)
            ver_1 = nodes.match(class_1, name=name_picture_1).first()
            ver_2 = nodes.match(class_2, name=name_picture_2).first()
            rel = Relationship(ver_1, relation, ver_2)
            self._graph.create(rel)
        except AttributeError:
            print('Введена не существующая вершина')

    def ret_rel_with_num(self, recog_photo_num: str) -> list:
        """
        Return list of vertex relation
        :param recog_photo_num: Recognized photo number
        :return: list
        """
        data_vertex = self._graph.query(f"match (n:ExistsNum)-[]->(p)"
                                        f"where n.name = \"{recog_photo_num}\" "
                                        f"return p.name").data()
        list_of_rel_data = []
        for dicts in data_vertex:
            list_of_rel_data.append(*dicts.values())
        return list_of_rel_data

    def search_exists_num(self, recog_photo_num: str) -> bool:
        """
        Finding a vertex with the same name with class ExistsNum
        :param recog_photo_num: Recognized photo number
        :return: bool
        """
        return True if NodeMatcher(self._graph).match("ExistsNum", name=recog_photo_num).exists() else False
