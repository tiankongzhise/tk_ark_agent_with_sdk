from pathlib import Path


if __name__ == '__main__':
    test = Path(__file__).parent
    print(type(test))
    print([test])
