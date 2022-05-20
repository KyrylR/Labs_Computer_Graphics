import math

from matplotlib import patches, pyplot as plt


def read_data_from_file(filepath: str):
    """
    Getting data with a list of points, as well as
    search points - points that define the search area

    :param filepath: path to data file
    :return: Tuple of: points list and search list
    """
    try:
        with open(filepath, mode='r+') as data_file:
            points_quantity, counter = -1, 0
            points_list = []
            search_list = []
            for line in data_file:
                if not line.startswith("#"):
                    if counter < 2:
                        value_list = list(map(int, line.split()))
                        search_list.append(Point(value_list[0], value_list[1]))
                        counter += 1
                        continue
                    value_list = list(map(int, line.split(" ")))
                    points_list.append(Point(value_list[1], value_list[2]))
                    points_quantity += 1

            return points_list, search_list
    except FileNotFoundError as err:
        print('File do not exist')
        raise err
    except IOError as err:
        print('IO error')
        raise err


class Point:
    """
    Default class of points with all interrelation
    operations for x and y, separately and for both
    """
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y > other.y

    def __lt__(self, other):
        return not (self.__gt__(other))

    def __le__(self, other):
        return not (self.__ge__(other))

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __str__(self):
        return "(%d,%d)" % (self.x, self.y)

    def __repr__(self):
        return "(%d,%d)" % (self.x, self.y)


class NodeData:
    __slots__ = ['left_index', 'right_index', 'sorted_y']

    def __init__(self, left: int, right: int, sorted_y: list):
        self.left_index = left
        self.right_index = right
        self.sorted_y = sorted_y

    def __repr__(self):
        return f"[{self.left_index}; {self.right_index}), {self.sorted_y}"


class Node:
    __slots__ = ['data', 'left', 'right']

    def __init__(self, data: NodeData = None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.data}"

    def graph_viz(self, string_mutable):
        if self is None:
            return

        string_mutable[0] += f"\"{self}\"\n"

        if self.left is not None:
            string_mutable[0] += f"\"{self}\" -> \"{self.left}\" [label = \"left\"]\n"
        if self.right is not None:
            string_mutable[0] += f"\"{self}\" -> \"{self.right}\" [label = \"right\"]\n"

        if self.left is not None:
            self.left.graph_viz(string_mutable)

        if self.right is not None:
            self.right.graph_viz(string_mutable)


def make_clusters(sorted_list):
    result_list = []
    temp_list = []
    for item in sorted_list:
        if len(temp_list) == 0 or temp_list[-1].x == item.x:
            temp_list.append(item)
        else:
            result_list.append(sorted(temp_list.copy(), key=lambda point: point.y))
            temp_list.clear()
            temp_list.append(item)
    return result_list


def get_cluster_x(cluster):
    val = cluster[0]
    return val.x


def get_cluster_y(cluster):
    val = cluster[0]
    return val.y


class SegmentTree:
    """
    Build segment tree of given points of type Point.
    """
    __slots__ = ['root', 'x_cords', 'y_cords', 'result', 'counter']

    def __init__(self, points_list: list, search_area: list):
        points_list = make_clusters(sorted(point_list, key=lambda point: point.x))
        self.root = self.build_tree(points_list, get_cluster_x(points_list[0]), get_cluster_x(points_list[-1]))
        self.x_cords = (min(search_area[0].x, search_area[1].x), max(search_area[0].x, search_area[1].x))
        self.y_cords = (min(search_area[0].y, search_area[1].y), max(search_area[0].y, search_area[1].y))
        self.result = []
        self.counter = 0

    def build_tree(self, points_list: list, left_index, right_index) -> Node:
        if len(points_list) == 1:
            return Node(NodeData(get_cluster_x(points_list[0]), get_cluster_x(points_list[-1]) + 1, points_list), None,
                        None)
        median = math.floor((1 + len(points_list)) / 2)
        left_list = points_list[:median]
        left = self.build_tree(left_list, get_cluster_x(points_list[0]), get_cluster_x(points_list[-1]))
        median = math.floor((1 + len(points_list)) / 2)
        right_list = points_list[median:]
        right = self.build_tree(right_list, get_cluster_x(points_list[0]), get_cluster_x(points_list[-1]))
        return Node(
            NodeData(get_cluster_x(points_list[0]), get_cluster_x(points_list[-1]) + 1, self.sort_by_y(points_list)),
            left, right)

    @staticmethod
    def sort_by_y(to_sort: list):
        return sorted(to_sort, key=lambda points: get_cluster_y(points))

    def query(self):
        search_root = self.root
        if search_root is None:
            return

        if search_root.left is None or search_root.right is None:
            self.check_segment_node(search_root)
            return

        while search_root.right.data.left_index >= self.x_cords[1]:
            search_root = search_root.left
            if search_root.right is None:
                self.check_segment_node(search_root)
                return

        while search_root.left.data.right_index <= self.x_cords[0]:
            search_root = search_root.right
            if search_root.left is None:
                self.check_segment_node(search_root)
                return

        self.query_left(search_root.left)
        self.query_right(search_root.right)

    def query_left(self, left_node: Node):
        if left_node.right is None:
            self.check_segment_node(left_node)
        if self.check_segment_node(left_node.right):
            self.query_left(left_node.left)

    def query_right(self, right_node: Node):
        if right_node.left is None:
            self.check_segment_node(right_node)
        if self.check_segment_node(right_node.left):
            self.query_right(right_node.right)

    @staticmethod
    def check_axis_y(to_check_y, down, up) -> bool:
        return down <= to_check_y <= up

    def check_segment_node(self, node: Node):
        # Add nested segments
        res = False
        self.counter += 1
        if node is None:
            return res
        if self.x_cords[0] <= node.data.left_index:
            if self.x_cords[1] >= node.data.right_index:
                res = True
                for item in node.data.sorted_y:
                    for cluster in item:
                        if self.check_axis_y(cluster.y, self.y_cords[0], self.y_cords[1]):
                            self.result.append(cluster)
            else:
                if node.right is not None:
                    self.query_right(node)
        else:
            if node.left is not None:
                self.query_left(node)
        return res

    def graph_viz(self):
        string = "digraph g {\n"
        wrapper = [string]

        self.root.graph_viz(wrapper)
        wrapper[0] += "}\n"

        with open("data/graph_viz.txt", mode='w+') as data_file:
            data_file.write(wrapper[0])

    def plot_points(self, figure, axes, points):
        for index, point in enumerate(points):
            axes.scatter([point.x], [point.y], color="red")
            axes.annotate(f"({point.x}; {point.y})", (point.x, point.y),
                          xytext=(point.x - 0.025, point.y + 0.1))

    def plot_region(self, axes, search_region):
        width = search_region[1].x - search_region[0].x
        height = search_region[1].y - search_region[0].y

        rect = patches.Rectangle((search_region[0].x, search_region[0].y), width, height, linewidth=1, edgecolor='b',
                                 facecolor='none')
        axes.add_patch(rect)


if __name__ == "__main__":
    point_list, search_list = read_data_from_file("data/data.txt")
    tree = SegmentTree(point_list, search_list)
    tree.query()
    print(f"Result(Points): {tree.result}")
    print(f"Result(Size): {len(tree.result)}")
    print(f"Counter: {tree.counter}")
    tree.graph_viz()

    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    tree.plot_points(figure, axes, sorted(point_list, key=lambda point: point.x))
    tree.plot_region(axes, search_list)
    plt.show()
