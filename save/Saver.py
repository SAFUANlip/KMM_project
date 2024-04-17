import os.path
import json
from Models import DispatcherSource, BaseSource, ControlPointSource, RadarSource, \
                    StartDeviceSource, AeroTargetSource

class Saver:
    def __init__(self, name_of_dir = 'save'):
        self.name_of_dir = name_of_dir
        '''
        создаем директорию если она не существует
        '''
        try:
            os.mkdir(self.name_of_dir)
        except Exception:
            pass

    def code_dispatcher(self, obj: DispatcherSource) -> dict:
        obj_dictionary = {
            'type': 'DispatcherSource',
            'time': obj.getTime()
        }
        return obj_dictionary

    def code_base(self, obj) -> dict:
        obj_dictionary = {
            'type': obj.__class__.__name__,
            'id': obj.id,
            'model_type': obj.model_type,
            'x': obj.getX(),
            'y': obj.getY(),
            'z': obj.getZ()
        }
        return obj_dictionary

    def code_radar(self, obj: RadarSource) -> dict:
        obj_dictionary = self.code_base(obj)
        obj_dictionary['overview_mode'] = obj.getOverviewMode()
        obj_dictionary['pan_start'] = obj.getPanStart()
        obj_dictionary['sector_type'] = obj.getSectorType()
        obj_dictionary['pan_angle'] = obj.getPanStart()
        return obj_dictionary

    def code_target(self, obj: AeroTargetSource) -> dict:
        obj_dictionary = self.code_base(obj)
        obj_dictionary['speed'] = obj.getSpeed()
        obj_dictionary['direction'] = obj.getDirection()
        obj_dictionary['time_start'] = obj.getTimeStart()
        obj_dictionary['time_finish'] = obj.getTimeFinish()
        return obj_dictionary

    def parse_type(self, obj) -> bool:
        return obj['type'] in ('DispatcherSource', 'BaseSource', 'ControlPointSource',
                               'RadarSource', 'StartDeviceSource', 'AeroTargetSource')

    def parse_dispatcher(self, obj: DispatcherSource):
        object = DispatcherSource()
        object.setTime(obj['time'])
        return object

    def parse_base(self, obj, type: str):
        if type == 'ControlPointSource':
            object = ControlPointSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'StartDeviceSource':
            object = StartDeviceSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'RadarSource':
            object = RadarSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'AeroTargetSource':
            object = AeroTargetSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
            print(object)
        object.setZ(obj['z'])
        return object

    def parse_radar(self, obj: RadarSource) -> dict:
        object = self.parse_base(obj, 'RadarSource')
        object.setSectorType(obj['sector_type'])
        object.setOverviewMode(obj['overview_mode'])
        object.setPanStart(obj['pan_start'])
        object.setPanAngle(obj['pan_angle'])
        return object

    def parse_target(self, obj: AeroTargetSource) -> dict:
        object = self.parse_base(obj, 'AeroTargetSource')
        object.setSpeed(obj['speed'])
        object.setDirection(obj['direction'])
        object.setTimeStart(obj['time_start'])
        object.setTimeFinish(obj['time_finish'])
        return object



    def saveObjects(self, list_of_objects: list, name_of_file: str):
        '''
        :param list_of_objects: - список объектов
        :param name_of_file: - название файла
        переводим объект в словарь
        создаём файл в нашей директории
        записываем каждый объект в файл в качестве json
        '''
        list_od_dicts = []
        for obj in list_of_objects:
            if (isinstance(obj, DispatcherSource)):
                obj_dictionary = self.code_dispatcher(obj)

            elif (isinstance(obj, (ControlPointSource, StartDeviceSource))):
                obj_dictionary = self.code_base(obj)

            elif (isinstance(obj, RadarSource)):
                obj_dictionary = self.code_radar(obj)

            elif (isinstance(obj, AeroTargetSource)):
                obj_dictionary = self.code_target(obj)

            list_od_dicts.append(obj_dictionary)

        with open(self.name_of_dir + '/' + name_of_file, 'w') as outfile:
            json.dump(list_od_dicts, outfile)
        return 0

    def uploadObjects(self, way_to_file: str):
            with open(way_to_file, 'r') as file:
                objects = json.load(file)

            uploaded_objects = []
            for obj in objects:
                if self.parse_type(obj):
                    if obj['type'] == 'DispatcherSource':
                        uploaded_objects.append(self.parse_dispatcher(obj))
                    elif obj['type'] == 'ControlPointSource':
                        uploaded_objects.append(self.parse_base(obj, 'ControlPointSource'))
                    elif obj['type'] == 'StartDeviceSource':
                        uploaded_objects.append(self.parse_base(obj, 'StartDeviceSource'))
                    elif obj['type'] == 'RadarSource':
                        uploaded_objects.append(self.parse_radar(obj))
                    elif obj['type'] == 'AeroTargetSource':
                        uploaded_objects.append(self.parse_target(obj))

            return uploaded_objects















