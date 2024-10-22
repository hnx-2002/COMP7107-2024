def compare_three_files(file1, file2, file3):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2, open(file3, 'r') as f3:
            f1.readline()
            f2.readline()
            f3.readline()
            line_number = 2
            while True:
                line1 = f1.readline()
                line2 = f2.readline()
                line3 = f3.readline()


                if not line1 and not line2 and not line3:
                    print("All three files are identical.")
                    return True


                if line1 != line2 or line2 != line3:
                    print(f"Difference found at line {line_number}:")
                    if line1 != line2:
                        print(f"File 1 and File 2 differ.\nFile 1: {line1}\nFile 2: {line2}")
                    if line2 != line3:
                        print(f"File 2 and File 3 differ.\nFile 2: {line2}\nFile 3: {line3}")
                    if line1 != line3:
                        print(f"File 1 and File 3 differ.\nFile 1: {line1}\nFile 3: {line3}")
                    return False

                line_number += 1
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False


def compare_two_files(file1, file2):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            line_number = 1
            while True:
                line1 = f1.readline()
                line2 = f2.readline()


                if not line1 and not line2:
                    print("All two files are identical.")
                    return True


                if line1 != line2:

                    print(f"Difference found at line {line_number}:")
                    print(f"File 1 and File 2 differ.\nFile 1: {line1}\nFile 2: {line2}")

                    return False

                line_number += 1
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False

def compare_three_html_files(file1, file2, file3):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2, open(file3, 'r') as f3:

            line1 = f1.readline().strip()
            line2 = f2.readline().strip()
            line3 = f3.readline().strip()
            line1 = f1.readline().strip()
            line2 = f2.readline().strip()
            line3 = f3.readline().strip()
            line1 = f1.readline().strip()
            line2 = f2.readline().strip()
            line3 = f3.readline().strip()
            line1 = f1.readline().strip()
            line2 = f2.readline().strip()
            line3 = f3.readline().strip()

            line_number = 1  # track line numbers

            while True:
                line1 = f1.readline().strip()
                line2 = f2.readline().strip()
                line3 = f3.readline().strip()

                # end and the same
                if not line1 and not line2 and not line3:
                    print("All three HTML files are identical.")
                    return True

                # some diff in certain line or len(file) diff
                if line1 != line2 or line2 != line3:
                    print(f"Difference found at line {line_number}:")
                    if line1 != line2:
                        print(f"File 1 and File 2 differ.\nFile 1: {line1}\nFile 2: {line2}")
                    if line2 != line3:
                        print(f"File 2 and File 3 differ.\nFile 2: {line2}\nFile 3: {line3}")
                    if line1 != line3:
                        print(f"File 1 and File 3 differ.\nFile 1: {line1}\nFile 3: {line3}")
                    return False

                line_number += 1
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False


# 示例调用
file1 = '../data/naive_query.txt'
file2 = '../data/pivots_query.txt'
file3 = '../data/iDistance_query.txt'

# html_file1 = '../data/iDistance_query_ɛ_0.8.html'
# html_file2 = '../data/Naive_query_ɛ_0.8.html'
# html_file3 = '../data/Pivots_query_ɛ_0.8.html'

html_file1 = '../data/Naive_KNN_K_10.html'
html_file2 = '../data/Pivots_KNN_K_10.html'
html_file3 = '../data/iDistance_KNN_K_10.html'


method = int(input())
if(method == 3):
    compare_three_files(file1, file2, file3)
elif(method == 0):
    compare_three_html_files(html_file1, html_file2, html_file3)
else:
    compare_two_files(file1, file2)