# This script visualizes the number of matching regular expressions of all .cpp and .h files in a directory tree via dot (graphhviz) 

import os
import pprint
import re


class DirWalker:
    def __init__(self):
        pass

    def walk(self, *args, **args_dict):
        return os.walk(*args, **args_dict)


class GraphFromDirectory:
    def __init__(self):
        self.dir_walker_ = DirWalker()
        self.edges_ = dict()
        self.nodes_ = dict()
        self.root_nodes_ = []
        self.next_id_ = 0

    def set_dir_walker(self, dir_walker):
        self.dir_walker_ = dir_walker

    def __get_node(self, name, nodes):
        if name in nodes:
            return nodes[name]
        else:
            vertex_idx = self.next_id_
            self.next_id_ += 1
            vertex_name = "node_%i" % (vertex_idx)
            nodes[name] = vertex_name
            return nodes[name]

    def __extract_edges_from_path(self, path, path_to_nodes, nodes):
        path_components = path.split(os.sep)
        edges = dict()
        for i in zip(
            range(0, len(path_components) - 1), range(1, len(path_components))
        ):
            # Get Components of path
            from_ = path_components[i[0]]
            to_ = path_components[i[1]]

            # Rebuild the path which has the component as its last element
            from_path = os.sep.join(path_components[0 : i[0] + 1])
            to_path = os.sep.join(path_components[0 : i[1] + 1])

            # Get unique node ids for each path
            from_node = self.__get_node(from_path, path_to_nodes)
            to_node = self.__get_node(to_path, path_to_nodes)

            # Store
            edges[from_node] = set([to_node])

            # the nodes dict points from node_ids to node info
            nodes[from_node] = {"name": from_, "path": from_path}
            nodes[to_node] = {"name": to_, "path": to_path}

        return edges

    def __update_edges(self, edges, additional_edges):
        edges_cpy = dict(edges)
        for k, v in additional_edges.items():
            if k in edges:
                edges_cpy[k].update(v)
            else:
                edges_cpy[k] = v
        return edges_cpy

    def add_dir(self, dir_name, ignore_contains):
        common_path, root_path = os.path.split(dir_name)
        path_to_nodes = dict()

        for root, dirs, files in self.dir_walker_.walk(dir_name, topdown=False):
            # only iterate the directories
            for act_dir in dirs:
                root_stripped = root.replace(common_path + os.sep, "")
                path = os.path.join(root_stripped, act_dir)

                ignore = False
                for i in ignore_contains:
                    if i in path:
                        ignore = True

                if ignore:
                    continue

                edges_of_path = self.__extract_edges_from_path(
                    path, path_to_nodes, self.nodes_
                )
                self.edges_ = self.__update_edges(self.edges_, edges_of_path)

        self.root_nodes_.append(path_to_nodes[root_path])

    def get_graph(self):

        local_edges = dict(self.edges_)
        local_nodes = dict(self.nodes_)

        root_node = "root"

        local_edges.update({root_node: set(self.root_nodes_)})
        local_nodes[root_node] = {"name": "root", "path": ".\\"}

        return root_node, local_edges, local_nodes


def generate_dot_file(edges, nodes):
    print("digraph D {")
    print('size ="40,40!";')
    print('rankdir="LR";')
    for k, i in nodes.items():

        if "occurences" in i:
            occ = i["occurences"]
            if occ == 0:
                fillcolor = "green"
            elif occ < 10:
                fillcolor = "yellow"
            else:
                fillcolor = "indianred1"
        else:
            occ = 0
            fillcolor = "green"

        if "files" in i:
            files = i["files"]
            if len(files) != 0:
                text = "<br/>" + "<br/>".join(files)
            else:
                text = ""
        else:
            text=""

        print(
            "  %s [fillcolor=%s, shape=folder,style=filled, label=<<font point-size='20'><b>%s</b> [%i]</font>%s>]"
            % (k, fillcolor, i["name"], occ, text)
        )

    print()
    for k, v in edges.items():
        print("  %s -> {%s}" % (k, ", ".join(v)))

    print("}")


def search_occurences_in_dir(path, regex):
    path = ".." + os.sep + ".." + os.sep + path

    files = [
        os.path.join(path, i)
        for i in os.listdir(path)
        if os.path.isfile(os.path.join(path, i))
    ]

    files_filtered = [i for i in files if ".cpp" in i or ".h" in i]
    cnt = 0
    occurences = []
    for i in files_filtered:
        with open(i, "r") as file:
            data = file.read()

        occ = len(regex.findall(data))
        _, filename = os.path.split(i)
        if occ > 0:
            occurences.append("%s [%i]" % (filename, occ))

        cnt += occ

    return cnt, occurences


if __name__ == "__main__":
    ignore_contains = ["external"]
    graph_from_dir = GraphFromDirectory()
    graph_from_dir.add_dir("..\\..\\bsl", ignore_contains)
    graph_from_dir.add_dir("..\\..\\drivers", ignore_contains)
    graph_from_dir.add_dir("..\\..\\hal", ignore_contains)

    root_node, edges, nodes = graph_from_dir.get_graph()

    regex = re.compile("drive_kernel::")
    for k, v in nodes.items():
        # root node should be omitted
        if k == "root":
            continue

        path = v["path"]

        cnt, occurences = search_occurences_in_dir(path, regex)
        nodes[k].update({"occurences": cnt, "files": occurences})

    # Write the dot file to stdout
    generate_dot_file(edges, nodes)
