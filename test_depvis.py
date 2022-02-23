from unittest.mock import MagicMock
from unittest import mock
from depvis import GraphFromDirectory


def create_GraphFromDirectory():
    graph_from_dir = GraphFromDirectory()

    return graph_from_dir


def test_add_dir_1Dir2FilesWalk_StateChange2EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()

    stub_dir_walker = MagicMock()
    stub_dir_walker.walk.return_value = [
        ["..\\..\\test", ["dir1"], ["file1"]],
        ["..\\..\\test\\dir1", [], ["file2"]],
    ]
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("..\\..\\test", [])

    # Assert
    root_node, edges, nodes = graph_from_dir.get_graph()
    assert root_node == "root"
    assert edges == {"node_0": {"node_1"}, "root": {"node_0"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "test"},
        "node_1": {"name": "dir1", "path": "test\\dir1"},
        "root": {"name": "root", "path": ".\\"},
    }


def test_add_dir_2Dirs2FilesWalk_StateChange3EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()
    stub_dir_walker = MagicMock()
    stub_dir_walker.walk.return_value = [
        ["..\\..\\test", ["dir1"], ["file1"]],
        ["..\\..\\test\\dir1", ["dir2"], ["file2"]],
        ["..\\..\\test\\dir1\\dir2", [], []],
    ]
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("..\\..\\test", [])

    # Assert
    root_node, edges, nodes = graph_from_dir.get_graph()
    assert root_node == "root"
    assert edges == {"node_0": {"node_1"}, "node_1": {"node_2"}, "root": {"node_0"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "test"},
        "node_1": {"name": "dir1", "path": "test\\dir1"},
        "node_2": {"name": "dir2", "path": "test\\dir1\\dir2"},
        "root": {"name": "root", "path": ".\\"},
    }


def test_add_dir_TwoDirectories_StateChange5EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()
    stub_dir_walker1 = MagicMock()
    stub_dir_walker1.walk.return_value = [
        ["..\\..\\test1", ["dir1"], ["file1"]],
        ["..\\..\\test1\\dir1", [], ["file2"]],
    ]
    stub_dir_walker2 = MagicMock()
    stub_dir_walker2.walk.return_value = [
        ["..\\..\\test2", ["dir1"], ["file1"]],
        ["..\\..\\test2\\dir1", ["dir2"], ["file2"]],
        ["..\\..\\test2\\dir1\\dir2", [], []],
    ]

    # Act
    graph_from_dir.set_dir_walker(stub_dir_walker1)
    graph_from_dir.add_dir("..\\..\\test1", [])

    graph_from_dir.set_dir_walker(stub_dir_walker2)
    graph_from_dir.add_dir("..\\..\\test2", [])

    # Assert
    root_node, edges, nodes = graph_from_dir.get_graph()
    assert root_node == "root"
    assert edges == {
        "node_0": {"node_1"},
        "node_2": {"node_3"},
        "node_3": {"node_4"},
        "root": {"node_0", "node_2"},
    }
    assert nodes == {
        "node_0": {"name": "test1", "path": "test1"},
        "node_1": {"name": "dir1", "path": "test1\\dir1"},
        "node_2": {"name": "test2", "path": "test2"},
        "node_3": {"name": "dir1", "path": "test2\\dir1"},
        "node_4": {"name": "dir2", "path": "test2\\dir1\\dir2"},
        "root": {"name": "root", "path": ".\\"},
    }
