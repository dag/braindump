import subprocess


def less(iterable):  # pragma: no cover (not quite sure how to test)
    proc = subprocess.Popen(['less', '-FRX'], stdin=subprocess.PIPE)
    with proc.stdin:
        for chunk in iterable:
            proc.stdin.write(chunk)
    proc.wait()
