import re
from depvis import GraphFromDirectory, generate_dot_file, gengraph_png_from_dotfile, traverse_dirgraph_dfs
from perf_criteria import PerfRegExMatches

if __name__ == "__main__":
    png_name = "drive_kernel.png"
    ignore_contains = ["Arduino","AutogenMatlab","Autotuning"]
    graph_from_dir = GraphFromDirectory(generate_root = False)
    graph_from_dir.add_dir(
        "..\\edes\\checkout\\software\\1194_edes\\drive_kernel", ignore_contains
    )

    edges, nodes = graph_from_dir.get_graph()

    regex = re.compile("bsl::|drivers::")
    perf_crit = PerfRegExMatches(regex)

    traverse_dirgraph_dfs(edges, nodes, perf_crit,"node_0")

    fontsize_rank = {1:200,2:50, 3:30}
    # Write the dot file to stdout
    with open("dirgraph.dot", "w") as fp:
        generate_dot_file(edges, nodes,layout="twopi",  fontsize_rank = fontsize_rank, size=(120,120), ranksep = [34.0, 18.0, 25.0, 2.0, 2.0],file=fp)


    gengraph_png_from_dotfile("dirgraph.dot", png_name)
    print("%s successfully generated"%(png_name))
