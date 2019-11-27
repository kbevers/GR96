from pathlib import Path
from dataclasses import dataclass
from math import sin
from math import cos

from pyproj import Transformer

COORDS = Path("data/timeseries/COORDINATES.txt")

@dataclass
class Station:
    name: str
    latitude: float
    longitude: float

class TimeSeries:

    def __init__(self, station: Station):
        self.station = station
        self.T = []
        self.dE = []
        self.dN = []
        self.dU = []
        self.dEe = []
        self.dNe = []
        self.dUe = []

        pipeline = (
            "+proj=pipeline "
            "+step +proj=unitconvert +xy_in=deg +xy_out=rad "
            "+step +proj=cart +ellps=GRS80"
        )
        self.cart = Transformer.from_pipeline(pipeline)

    def add_entry(self, T, N, Ne, E, Ee, U, Ue):
        self.T.append(float(T))
        self.dN.append(float(N))
        self.dE.append(float(E))
        self.dU.append(float(U))
        self.dNe.append(float(Ne))
        self.dEe.append(float(Ee))
        self.dUe.append(float(Ue))

    def neu2xyz(self, dN, dE, dU):
        '''
        Convert from NEU-space to cartesian XYZ-space.

        NEU -> XYZ formula described in

        Nørbech, T., et al, 2003(?), "Transformation from a Common Nordic Reference
        Frame to ETRS89 in Denmark, Finland, Norway, and Sweden – status report"
        '''
        lat = self.station.latitude
        lon = self.station.longitude
        dX = -sin(lat)*cos(lon)*dN - sin(lon)*dE + cos(lat)*cos(lon)*dU
        dY = -sin(lat)*sin(lon)*dN + cos(lon)*dE + cos(lat)*sin(lon)*dU
        dZ = cos(lat)*dN + sin(lat)*dU

        return (dX, dY, dZ)



    def plot_neu():
        pass

    @property
    def N(self):
        return self.dN

    @property
    def E(self):
        return self.dE

    @property
    def U(self):
        return self.dU

    @property
    def XYZ(self):
        coord = (self.station.longitude, self.station.latitude, 0)
        (x, y, z) = self.cart.transform(*coord)
        for (n,e,u) in zip(self.dN, self.dE, self.dU):
            (dx, dy, dz) = self.neu2xyz(n, e, u)
            yield (x+dx, y+dy, z+dz)
        print(x,y,z)




stations = {}
with open(COORDS) as f:
    for line in f.readlines():
        if line.startswith("#"):
            continue
        (name, lat, lon) = line.strip().split()
        stations[name] = Station(name, float(lat), float(lon))


#read times series
time_series = {}
for path in Path("data/timeseries").glob("*_NEU.txt"):
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("%"):
                if line.startswith("% site name"):
                    site = line.split(":")[1].strip()
                    time_series[site] = TimeSeries(stations[site])
                continue

            time_series[site].add_entry(*line.split())

