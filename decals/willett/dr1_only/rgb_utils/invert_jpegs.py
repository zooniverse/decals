import os
from multiprocessing import Value, Lock
from multiprocessing.dummy import Pool as ThreadPool

import PIL.ImageOps
import progressbar as pb
from PIL import Image

widgets = ['Inverting: ', pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'), ' ', pb.ETA()]
cdx = 0
pbar = 0
class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()
    def change_value(self,v):
        with self.lock:
            self.val.value = v
    def increment(self):
        with self.lock:
            self.val.value += 1
    def value(self):
        with self.lock:
            return self.val.value

def invert_jpegs(fn, base_dir, inverted_dir):
    if '.jpeg' in fn:
        in_file = '{0}/{1}'.format(base_dir, fn)
        out_file = '{0}/{1}'.format(inverted_dir, fn)
        if not os.path.isfile(out_file):
            image = Image.open(in_file)
            inverted_image = PIL.ImageOps.invert(image)
            inverted_image.save(out_file)
    cdx.increment()
    pbar.update(cdx.value())

class function_wrapper(object):
    def __init__(self, f, args, kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs
    def __call__(self, x):
        return self.f(x, *self.args, **self.kwargs)

if __name__ == "__main__":
    #dr2 images
    print 'dr2'
    file_names = os.listdir('../jpeg/dr2')
    cdx=Counter(0)
    pbar = pb.ProgressBar(widgets=widgets, maxval=len(file_names))
    invert_dr2 = function_wrapper(invert_jpegs, ['../jpeg/dr2', '../jpeg/dr2_inverted'], {})
    pool=ThreadPool(4)
    pbar.start()
    results = pool.map(invert_dr2, file_names)
    pbar.finish()
    pool.close()
    pool.join()
    print '==============='

    #nsa_not_gz images
    print 'nsa'
    file_names = os.listdir('../jpeg/nsa_not_gz')
    cdx=Counter(0)
    pbar = pb.ProgressBar(widgets=widgets, maxval=len(file_names))
    invert_nsa = function_wrapper(invert_jpegs, ['../jpeg/nsa_not_gz', '../jpeg/nsa_not_gz_inverted'], {})
    pool=ThreadPool(4)
    pbar.start()
    results = pool.map(invert_nsa, file_names)
    pbar.finish()
    pool.close()
    pool.join()
    print '==============='
