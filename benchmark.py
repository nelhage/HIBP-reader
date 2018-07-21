import hashdb.raw_reader
import os
import base64
import time

N = 5000

reader = hashdb.raw_reader.RawReader.from_file('pwned-passwords-ordered-by-hash.txt')
reader.build_index()

keys = [
    base64.b16encode(os.urandom(20))
    for i in range(N)
]

timings = []
queries = []
top = time.time()
for (i, k) in enumerate(keys):
    if i % 1000 == 0:
        print("i={} elapsed={:.2f}s".format(i, time.time() - top))
    reader.queries = 0
    start = time.time()
    reader.query(k)
    end = time.time()
    timings.append(1000 * (end - start))
    queries.append(reader.queries)

print("searched {} keys...".format(len(timings)))
print("avg={:0.2f}ms".format(sum(timings)/len(timings)))
timings.sort()
print("min={:0.2f}ms".format(timings[0]))
print("p50={:0.2f}ms".format(timings[len(timings)*50//100]))
print("p90={:0.2f}ms".format(timings[len(timings)*90//100]))
print("p99={:0.2f}ms".format(timings[len(timings)*99//100]))
print("max={:0.2f}ms".format(timings[-1]))

queries.sort()
print("average queries={:.1f}".format(sum(queries)/len(queries)))
print("p90 queries={}".format(queries[len(queries)*99//100]))
print("max queries={}".format(max(queries)))
