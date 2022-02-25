# This script visualizes the number of matching regular expressions of all .cpp and .h files in a directory tree via dot (graphhviz)

import os
import pprint
import re
import sys
import subprocess


class DirWalker:
    def __init__(self):
        pass

    def walk(self, *args, **args_dict):
        return os.walk(*args, **args_dict)


class GraphFromDirectory:
    def __init__(self, generate_root=True):
        self.dir_walker_ = DirWalker()
        self.edges_ = dict()
        self.nodes_ = dict()
        self.root_nodes_ = []
        self.next_id_ = 0
        self.generate_root_ = generate_root

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

    def __append_edges_from_path(self, common_path, reduced_path, reduced_path_to_node):
        reduced_path_comp = reduced_path.split(os.sep)

        for i in zip(
            range(0, len(reduced_path_comp) - 1), range(1, len(reduced_path_comp))
        ):
            # Get Components of reduced_path
            from_ = reduced_path_comp[i[0]]
            to_ = reduced_path_comp[i[1]]

            # Rebuild the path which has the component as its last element
            from_path = os.sep.join(reduced_path_comp[0 : i[0] + 1])
            to_path = os.sep.join(reduced_path_comp[0 : i[1] + 1])

            # Get unique node ids for each path
            from_node = self.__get_node(from_path, reduced_path_to_node)
            to_node = self.__get_node(to_path, reduced_path_to_node)

            # Load/Modify/Store
            node_ref = self.edges_.get(from_node, set())
            node_ref.add(to_node)
            self.edges_[from_node] = node_ref

            # the nodes dict points from node_ids to node info
            self.nodes_[from_node] = {
                "name": from_,
                "path": common_path + os.sep + from_path,
                "rank": len(from_path.split(os.sep)),
            }
            self.nodes_[to_node] = {
                "name": to_,
                "path": common_path + os.sep + to_path,
                "rank": len(to_path.split(os.sep)),
            }

    def add_dir(self, dir_name, ignore_contains):
        common_path, root_path = os.path.split(dir_name)
        reduced_path_to_node = dict()

        for root, dirs, files in self.dir_walker_.walk(dir_name, topdown=False):
            # only iterate the directories
            for act_dir in dirs:
                root_reduced = root.replace(common_path + os.sep, "")
                reduced_path = os.path.join(root_reduced, act_dir)

                ignore = False
                for i in ignore_contains:
                    if i in reduced_path:
                        ignore = True

                if ignore:
                    continue

                edges_of_path = self.__append_edges_from_path(
                    common_path, reduced_path, reduced_path_to_node
                )

        self.root_nodes_.append(reduced_path_to_node[root_path])

    def get_graph(self):
        local_edges = dict(self.edges_)
        local_nodes = dict(self.nodes_)

        if self.generate_root_:
            root_node = "root"

            local_edges.update({root_node: set(self.root_nodes_)})
            local_nodes[root_node] = {"name": "root", "path": ".\\", "rank" : 0}

        return local_edges, local_nodes


def traverse_dirgraph_dfs(edges, nodes, callback, startnode="root"):
    nodes_not_visited = [startnode]
    while len(nodes_not_visited) != 0:
        node_id = nodes_not_visited.pop(0)

        children = list(edges.get(node_id, set()))
        children.sort()  # sort list because order in set is not defined
        nodes_not_visited = children + nodes_not_visited

        node = nodes[node_id]

        result = callback(node_id, node)
        nodes[node_id].update(result)


def generate_dot_file(
    edges, nodes, layout="dot", fontsize_rank= {}, nodesep=0.5, ranksep=0.5, size=(80, 80), file=sys.stdout
):
    print("graph D {", file=file)
    print("layout = %s" % (layout), file=file)
    # print("ranksep=6;", file=file)
    # print("ratio=auto;", file=file)
    # print("overlap=false", file=file)
    print("nodesep=%f;" % nodesep, file=file)

    if isinstance(ranksep, list):
        list_str = " ".join([str(i) for i in ranksep])
        print('ranksep="%s";' % (list_str), file=file)
    else:
        print('ranksep="%s";' % ranksep, file=file)

    print('size ="%i, %i!";' % (size[0], size[1]), file=file)
    print('rankdir="LR";', file=file)
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
            text = ""

        rank = i["rank"]
        if rank in fontsize_rank:
            fontsize = fontsize_rank[rank]
        else:
            fontsize = 20
        print(
            "  %s [fillcolor=%s, shape=folder,style=filled, label=<<font point-size='%i'><b>%s</b> [%i]</font>%s>]"
            % (k, fillcolor, fontsize, i["name"], occ, text),
            file=file,
        )

    print()
    for k, v in edges.items():
        print("  %s -- {%s}" % (k, ", ".join(v)), file=file)

    print("}", file=file)


def gengraph_png_from_dotfile(filename_dot, filename_png):
    run_re = subprocess.run(
        "dot.exe %s -T png -o %s" % (filename_dot, filename_png), capture_output=True
    )
    if run_re.returncode != 0:
        raise Exception("Running dot.exe failed", run_re.stderr)


if __name__ == "__main__":
    pass
