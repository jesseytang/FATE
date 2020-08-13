from pipeline.backend.config import Backend
from pipeline.backend.config import WorkMode
from pipeline.backend.pipeline import PipeLine
from pipeline.component.dataio import DataIO
from pipeline.component.hetero_lr import HeteroLR
from pipeline.component.intersection import Intersection
from pipeline.component.reader import Reader
from pipeline.interface.data import Data

guest = 9999
hosts = [10000, 10001]
arbiter = 10002

guest_train_data = {"name": "hetero_breast_guest", "namespace": "experiment"}
host_train_data = [{"name": "hetero_breast_host", "namespace": "experiment"},
                   {"name": "hetero_breast_host", "namespace": "experiment"}]

pipeline = PipeLine().set_initiator(role='guest', party_id=9999).set_roles(guest=9999, host=hosts, arbiter=arbiter)

reader_0 = Reader(name="reader_0")
reader_0.get_party_instance(role='guest', party_id=guest).algorithm_param(table=guest_train_data)
reader_0.get_party_instance(role='host', party_id=hosts[0]).algorithm_param(table=host_train_data[0])
reader_0.get_party_instance(role='host', party_id=hosts[1]).algorithm_param(table=host_train_data[1])

dataio_0 = DataIO(name="dataio_0")

dataio_0.get_party_instance(role='guest', party_id=9999).algorithm_param(with_label=True, output_format="dense")
dataio_0.get_party_instance(role='host', party_id=[10000, 10001]).algorithm_param(with_label=False)

intersect_0 = Intersection(name="intersection_0")
hetero_lr_0 = HeteroLR(name="hetero_lr_0", early_stop="weight_diff")

pipeline.add_component(reader_0)
pipeline.add_component(dataio_0, data=Data(data=reader_0.output.data))
pipeline.add_component(intersect_0, data=Data(data=dataio_0.output.data))
pipeline.add_component(hetero_lr_0, data=Data(train_data=intersect_0.output.data))

# pipeline.set_deploy_end_component([dataio_0])
# pipeline.deploy_component([dataio_0])

pipeline.compile()

pipeline.fit(backend=Backend.EGGROLL, work_mode=WorkMode.STANDALONE)

print(pipeline.get_component("intersection_0").get_output_data())
print(pipeline.get_component("dataio_0").get_model_param())
print(pipeline.get_component("hetero_lr_0").get_model_param())


# predict

pipeline.predict(backend=Backend.EGGROLL, work_mode=WorkMode.STANDALONE)