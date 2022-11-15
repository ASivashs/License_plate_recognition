from py2neo import Graph, Node, Relationship, Subgraph
from py2neo.matching import *
from typing import NoReturn
from help_func.help_func import is_not_blank
import os

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

    def __update_data_before_change(self) -> NoReturn:
        self._data_before_change = self._graph.query("MATCH (n) RETURN (n)").to_ndarray()

    def __find_vertex_after_change(self) -> str:
        """
        Find new add vertex
        :return: find new Node
        """
        set_before_change = set(self.__convert_list(self._data_before_change))
        set_after_change = set(self.__convert_list(self._graph.query("MATCH (n) RETURN (n)").to_ndarray()))
        inter_sec_set = set_after_change.difference(set_before_change).pop()
        self.__update_data_before_change()
        try:
            return NodeMatcher(self._graph).match(name=inter_sec_set).first(), inter_sec_set
        except KeyError:
            print("Не было обнаружено новой вершины")

    def __add_photo_with_relation_ver_intersec(self, dict_data: dict) -> NoReturn:
        """
        Add name_photo with relations
        :param dict_data: dict key can be: NUM_AUTO, COLOR, MARK
        :return: None
        """
        list_of_nodes, list_of_relations = [], []
        main_node, name_main_node = self.__find_vertex_after_change()
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
        self.__create_rel_exist_and_add_vertex(name_main_node)

    def __create_rel_exist_and_add_vertex(self, name_node: str) -> bool:
        """
        Create relation between recognize number and exist number
        :param name_node name photo node that find number
        :return: bool
        """
        nodes = NodeMatcher(self._graph)
        recog_num_photo = self._graph.query(f"match (n:Photo) - [:NUM_AUTO] -> (auto_num) "
                                            f"where n.name = \"{name_node}\" "
                                            f"return auto_num.name").evaluate()
        try:
            ver_1 = nodes.match("Photo_data", name=recog_num_photo).first()
            ver_2 = nodes.match("ExistsNum", name=recog_num_photo).first()
            rel = Relationship(ver_1, "ALLOW_ENTER", ver_2)
            self._graph.create(rel)
            return True
        except AttributeError:
            return False

    def print_all_data(self) -> NoReturn:
        print(self._graph.query(
            "MATCH (n)-[rel]->(p)"
            "RETURN n.name as vert_1, type(rel) as relation, p.name as vert_2").to_data_frame())
        print(self._graph.query(
            "MATCH (n)"
            "WHERE NOT (n)-[]->() and not ()-[]->(n)"
            "RETURN n.name as standalone_vert").to_data_frame())

    def add_new_node_photo(self, name_picture: str, func_recognize) -> NoReturn:
        """
        Add new node in DB
        :param name_picture: name of vertex
        :param func_recognize: func that recognize data from photo
        :return: None
        """
        if not NodeMatcher(self._graph).match("Photo", name=name_picture).exists():
            new_node = Node("Photo", name=os.path.basename(name_picture))
            self._graph.create(new_node)
            res_recognize = func_recognize(name_picture)[1]
            if is_not_blank(res_recognize):
                print("Фотография добавлена, но не обработана")
            else:
                dict_data = {"NUM_AUTO": res_recognize, }
                self.__add_photo_with_relation_ver_intersec(dict_data=dict_data)
        else:
            print("Такая ссылка на фотографию уже существует")

    def add_num_auto_for_entry(self, num_auto: str, first_name_: str, last_name_: str) -> bool:
        """
        Add new num auto for entry in DB, also first name, last name
        :param num_auto: uniq num auto
        :param first_name_: first name driver
        :param last_name_: last name driver
        :return: None
        """
        if not NodeMatcher(self._graph).match("ExistsNum", name=num_auto).exists():
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
            print('Такой номер на въезд уже существует')
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

    def find_and_choose(self, recog_photo_num: str) -> dict:
        """
        Find vertex in class ExistsNum and return his data
        :param recog_photo_num: Recognized photo number
        :return: dict
        """
        if NodeMatcher(self._graph).match("ExistsNum", name=recog_photo_num).exists():
            return self.ret_rel_with_num(recog_photo_num)

    def ret_rel_with_num(self, recog_photo_num: str) -> dict:
        """
        Return list of vertex relation
        :param recog_photo_num: Recognized photo number
        :return: list
        """
        data_vertex = self._graph.query(f"match (n:ExistsNum)-[rel]->(p)"
                                        f"where n.name = \"{recog_photo_num}\" "
                                        f"return type(rel), p.name").data()
        dict_of_data_driver = {list(dicts.values())[0]: list(dicts.values())[1] for dicts in data_vertex}
        return dict_of_data_driver

    def search_exists_num(self, recog_photo_num: str) -> bool:
        """
        Finding a vertex with the same name with class ExistsNum
        :param recog_photo_num: Recognized photo number
        :return: bool
        """
        return True if NodeMatcher(self._graph).match("ExistsNum", name=recog_photo_num).exists() else False

    def get_all_add_drivers(self):
        data_vertex = self._graph.query("match (n:ExistsNum)"
                                        "return n.name").to_ndarray()
        return data_vertex
