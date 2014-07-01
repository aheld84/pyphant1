from pyphant.core.Worker import Worker, plug
from pyphant.core.Connectors import TYPE_IMAGE
from pyphant.core.DataContainer import FieldContainer
from pyphant.core.Helpers import parseFCUnit
from copy import deepcopy
from numpy.random import normal


class AddNoise(Worker):
    name = "Add Noise"
    _sockets = [("input_fc", TYPE_IMAGE)]
    _params = [("width", u"standard deviation", "1.0", None)]

    @plug(TYPE_IMAGE)
    def add_noise(self, input_fc, subscriber=0):
        width = parseFCUnit(self.paramWidth.value)
        scale = float(width / input_fc.unit)
        noisy_data = input_fc.data + normal(
            scale=scale, size=input_fc.data.shape
            )
        output_fc = FieldContainer(
            data=noisy_data,
            unit=deepcopy(input_fc.unit),
            dimensions=deepcopy(input_fc.dimensions),
            longname=input_fc.longname + u" with noise",
            shortname=input_fc.shortname,
            error=deepcopy(input_fc.error),
            mask=deepcopy(input_fc.mask),
            attributes=deepcopy(input_fc.attributes)
            )
        output_fc.seal()
        return output_fc
