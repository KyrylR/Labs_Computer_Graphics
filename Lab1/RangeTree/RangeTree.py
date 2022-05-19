import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Point:
    """
    Default class of points with all interrelation
    operations for x and y, separately and for both
    """
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def grater_only_x(self, other):
        return self.x > other.x

    def grater_only_y(self, other):
        return self.y > other.y

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

    def __init__(self, left=None, right=None, sorted_y=None):
        self.left_index = left
        self.right_index = right
        self.sorted_y = sorted_y

    def __repr__(self):
        return f"[{self.left_index}; {self.right_index}), {self.sorted_y}"


class Node:
    __slots__ = ['data', 'left', 'right']

    def __init__(self, data: NodeData = None, left=None, right=None):
        self.data = data
        self.left: Node = left
        self.right: Node = right

    def __repr__(self):
        return f"({self.data})"

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


class Tree:
    __slots__ = ['root', 'sorted_array']

    def __init__(self, points: list = None):
        self.root: Node = None
        self.sorted_array = sorted(points, key=lambda point: point.x)
        y_points = sorted(points, key=lambda point: point.y)

        for i in range(len(y_points)):
            y_points[i] = self.sorted_array.index(y_points[i])

        print(f"Points: {points}")
        self.root = self.build(y_points, 0, len(points))

    def build(self, y_indexes: list, left_index, right_index):
        if int((right_index - left_index) / 2) < 1:
            return Node(NodeData(left_index, right_index, y_indexes))

        node = Node(NodeData(left_index, right_index, y_indexes))
        median = int((left_index + right_index) / 2)
        left_son_y = []
        right_son_y = []

        for i in range(len(y_indexes)):
            if y_indexes[i] < median:
                left_son_y.append(y_indexes[i])
            else:
                right_son_y.append(y_indexes[i])

        left_son = self.build(left_son_y, left_index, median)
        right_son = self.build(right_son_y, median, right_index)

        node.left = left_son
        node.right = right_son

        return node

    def find(self, search_list):
        left_bound = -1
        right_bound = -1

        for i in range(len(self.sorted_array)):
            if left_bound == -1 and search_list[0].x <= self.sorted_array[i].x:
                left_bound = i
                continue
            if self.sorted_array[i].x > search_list[1].x:
                right_bound = i
                break

        if right_bound == -1:
            right_bound = len(self.sorted_array)

        result_nodes = []
        self.find_recursive(left_bound, right_bound, self.root, result_nodes)

        result_points = []

        for node in result_nodes:
            for y_index in node.data.sorted_y:
                if search_list[0].y <= self.sorted_array[y_index].y <= search_list[1].y:
                    result_points.append(self.sorted_array[y_index])

        return result_points

    def find_recursive(self, left_bound, right_bound, node: Node, result_array):
        left_index = node.data.left_index
        right_index = node.data.right_index
        median = int((left_index + right_index) / 2)

        if node.left is None and node.right is None:
            result_array.append(node)
            return

        if left_bound == left_index:
            if right_bound >= right_index:
                result_array.append(node)
                return
            if right_bound <= median:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                return
            else:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                self.find_recursive(left_bound, right_bound, node.right, result_array)
                return
        elif left_bound < left_index:
            if right_bound <= median:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                return
            elif right_bound == right_index:
                result_array.append(node)
                return
            elif right_bound > median:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                self.find_recursive(left_bound, right_bound, node.right, result_array)
                return
            else:
                return
        elif left_bound < median:
            if right_bound <= median:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                return
            else:
                self.find_recursive(left_bound, right_bound, node.left, result_array)
                self.find_recursive(left_bound, right_bound, node.right, result_array)
                return
        elif median <= left_bound < right_index:
            self.find_recursive(left_bound, right_bound, node.right, result_array)
            return
        else:
            return

    def graph_viz(self):
        string = "digraph g {\n"
        wrapper = [string]

        self.root.graph_viz(wrapper)
        wrapper[0] += "}\n"

        with open("data/graph_viz.txt", mode='w+') as data_file:
            data_file.write(wrapper[0])

    def plot_points(self, figure, axes):
        for index, point in enumerate(self.sorted_array):
            axes.scatter([point.x], [point.y], color="red")
            axes.annotate(f"({index}) ({point.x}; {point.y})", (point.x, point.y),
                          xytext=(point.x - 0.025, point.y + 0.1))

    def plot_region(self, axes, search_region):
        width = search_region[1].x - search_region[0].x
        height = search_region[1].y - search_region[0].y

        rect = patches.Rectangle((search_region[0].x, search_region[0].y), width, height, linewidth=1, edgecolor='b', facecolor='none')
        axes.add_patch(rect)


def read_data_from_file(filepath: str):
    """
    Getting data with a list of points, as well as
    search points - points that define the search area

    :param filepath: path to data file
    :return: Tuple of: points list and search list
    """
    try:
        with open(filepath, mode='r+') as data_file:
            init_val = False
            points_quantity, counter = -1, 0
            points_list = []
            search_list = []
            for line in data_file:
                if not line.startswith("#"):
                    if not init_val:
                        points_quantity = int(line.strip())
                        init_val = True
                        continue
                    if counter < points_quantity:
                        value_list = list(map(int, line.split(" ")))
                        points_list.append(Point(value_list[0], value_list[1]))
                        counter += 1
                        continue
                    value_list = list(map(int, line.split()))
                    search_list.append(Point(value_list[0], value_list[1]))

            return points_list, search_list
    except FileNotFoundError as err:
        print('File do not exist')
        raise err
    except IOError as err:
        print('IO error')
        raise err


if __name__ == "__main__":
    point_list, search_list = read_data_from_file("data/data.txt")
    tree = Tree(point_list)
    tree.graph_viz()
    print(tree.find(search_list))

    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    tree.plot_points(figure, axes)
    tree.plot_region(axes, search_list)
    plt.show()
