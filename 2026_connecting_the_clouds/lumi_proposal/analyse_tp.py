import glob
import os

class Count:
    def __init__(self):
        self.sum = 0
        self.N = 0

    def add(self, value):
        self.sum += value
        self.N += 1

    def mean(self):
        return self.sum / self.N

prog_3d = ('thl', 'qt', 'qt', 'qg', 'qs', 'u', 'v', 'w')

dirs = glob.glob('*')
for d in dirs:
    if os.path.isdir(d):
        subdirs = glob.glob(f'{d}/*')
        for sd in subdirs:
            out = glob.glob(f'{sd}/mhh*.out')[0]

            save_3d = Count()
            load_3d = Count()
            save_xy = Count()
            save_xz = Count()

            with open(out, 'r') as f:
                for l in f.readlines():

                    if 'Saving' in l and 'GB/s' in l:
                        field = l.split('"')[1].split('.')[0]
                        if field in prog_3d:
                            tp = float(l.split(' ')[-2])
                            save_3d.add(tp)

                    if 'Loading' in l and 'GB/s' in l:
                        field = l.split('"')[1].split('.')[0]
                        if field in prog_3d:
                            tp = float(l.split(' ')[-2])
                            load_3d.add(tp)

                    if 'xy' in l and 'GB/s' in l:
                        tp = float(l.split(' ')[-2])
                        save_xy.add(tp)

                    if 'xz' in l and 'GB/s' in l:
                        tp = float(l.split(' ')[-2])
                        save_xz.add(tp)


            print(f'{d:20s}: load 3D = {load_3d.mean():6.2f} GB/s, save 3D = {save_3d.mean():6.2f} GB/s, save xy = {save_xy.mean():6.2f} GB/s, save xz = {save_xz.mean():6.2f} GB/s')




