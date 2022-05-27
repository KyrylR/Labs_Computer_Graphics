import sys
import numpy as np
from scipy.spatial import ConvexHull


def main():
    try:
        n = int(sys.argv[1])
        low = int(sys.argv[2])
        high = int(sys.argv[3])
        points = np.random.randint(low, high, size=(n, 2))

        print('Generated ' + str(n) + ' random (x, y) coordinates. Each coordinate between ' + str(low) + ' and ' + str(
            high) + '.')
        """print('Generating convex hull...')
        hull = ConvexHull(points)
        print('Convex hull generated!\nPrinting to output file...')"""

        outputfilename = str(n) + 'points'
        outpf = open(outputfilename, 'w')

        # outpf.write(str(hull.vertices.size) + '\n')
        # outpf.write(str(n) + '\t' + str(low) + '\t' + str(high) + '\n')

        for p in points:
            outpf.write(str(p[0]) + '\t' + str(p[1]) + '\n')

        outpf.close()

        print('Done! File saved as ' + outputfilename)
        """showpoly = raw_input('Want to see how your polygon came out? (y/n): ')
        if(showpoly == 'y'):
            import matplotlib.pyplot as plt
            for simplex in hull.simplices:
                plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
            plt.show()
        else:
            print('We\'re ready then. Bye! :)')"""

    except IndexError:
        print('Not enough arguments. 3 arguments needed.\nUse:\n\
        python pointsGen.py <n of points> <lower int> <higher int>')
    except ValueError:
        print('All arguments must be integers:\nFirst argument is number of points in mesh.\n\
        Second and third arguments are lower and higher limits for random number in coordinates.\nUse:\n\
        python pointsGen.py <n of points> <lower int> <higher int>')
    except:
        print('Unexpected error: ', sys.exc_info()[0])
        raise


if __name__ == "__main__":
    main()
