import re
from depvis import GraphFromDirectory, generate_dot_file, gengraph_png_from_dotfile, traverse_dirgraph_dfs
from perf_criteria import PerfRegExMatches

if __name__ == "__main__":
    png_name = "bsl_drivers.png"
    ignore_contains = ["external"]
    graph_from_dir = GraphFromDirectory()
    graph_from_dir.add_dir(
        "..\\edes\\checkout\\software\\1194_edes\\bsl", ignore_contains
    )
    graph_from_dir.add_dir(
        "..\\edes\\checkout\\software\\1194_edes\\drivers", ignore_contains
    )
    graph_from_dir.add_dir(
        "..\\edes\\checkout\\software\\1194_edes\\hal", ignore_contains
    )

    edges, nodes = graph_from_dir.get_graph()

    regex = re.compile("drive_kernel::")
    perf_crit = PerfRegExMatches(regex)

    traverse_dirgraph_dfs(edges,nodes, perf_crit)

    # Write the dot file to stdout
    with open("dirgraph.dot", "w") as fp:
        generate_dot_file(edges, nodes, size=(20,20), file=fp)


    gengraph_png_from_dotfile("dirgraph.dot", png_name)
    print("%s successfully generated"%(png_name))
