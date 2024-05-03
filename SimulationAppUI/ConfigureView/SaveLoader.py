# Made by Alina
#
# https://github.com/SAFUANlip/KMM_project/blob/Alina/save/Saver.py
#

import os.path
import json
from SimulationAppUI.ConfigureView.Models import *

class SaveLoader:
    @staticmethod
    def code_dispatcher(obj: DispatcherSource) -> dict:
        obj_dictionary = {
            'type': 'DispatcherSource',
            'time': obj.getTime()
        }
        return obj_dictionary

    @staticmethod
    def code_base(obj) -> dict:
        obj_dictionary = {
            'type': obj.__class__.__name__,
            'id': obj.id,
            'model_type': obj.model_type,
            'x': obj.getX(),
            'y': obj.getY(),
            'z': obj.getZ()
        }
        return obj_dictionary

    @staticmethod
    def code_radar(obj: RadarSource) -> dict:
        obj_dictionary = SaveLoader.code_base(obj)
        obj_dictionary['overview_mode'] = obj.getOverviewMode()
        obj_dictionary['pan_start'] = obj.getPanStart()
        obj_dictionary['sector_type'] = obj.getSectorType()
        obj_dictionary['pan_angle'] = obj.getPanAngle()
        return obj_dictionary

    @staticmethod
    def code_target(obj: AeroTargetSource) -> dict:
        obj_dictionary = SaveLoader.code_base(obj)
        obj_dictionary['speed'] = obj.getSpeed()
        obj_dictionary['direction'] = obj.getDirection()
        obj_dictionary['time_start'] = obj.getTimeStart()
        obj_dictionary['time_finish'] = obj.getTimeFinish()

        track = list()
        for point in obj.track.points:
            track.append([point.getX(), point.getY(), point.getZ()])
        obj_dictionary['track'] = track

        return obj_dictionary

    @staticmethod
    def parse_type(obj) -> bool:
        return obj['type'] in ('DispatcherSource', 'BaseSource', 'ControlPointSource',
                               'RadarSource', 'StartDeviceSource', 'AeroTargetSource')

    @staticmethod
    def parse_dispatcher(obj: DispatcherSource):
        object = DispatcherSource()
        object.setTime(obj['time'])
        return object

    @staticmethod
    def parse_base(obj, type: str):
        if type == 'ControlPointSource':
            object = ControlPointSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'StartDeviceSource':
            object = StartDeviceSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'RadarSource':
            object = RadarSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        elif type == 'AeroTargetSource':
            object = AeroTargetSource(obj['id'], obj['model_type'], obj['x'], obj['y'])
        object.setZ(obj['z'])
        return object

    @staticmethod
    def parse_radar(obj: RadarSource) -> dict:
        object = SaveLoader.parse_base(obj, 'RadarSource')
        object.setSectorType(obj['sector_type'])
        object.setOverviewMode(obj['overview_mode'])
        object.setPanStart(obj['pan_start'])
        object.setPanAngle(obj['pan_angle'])
        return object

    @staticmethod
    def parse_target(obj: AeroTargetSource) -> dict:
        object = SaveLoader.parse_base(obj, 'AeroTargetSource')
        object.setSpeed(obj['speed'])
        object.setDirection(obj['direction'])
        object.setTimeStart(obj['time_start'])
        object.setTimeFinish(obj['time_finish'])
        
        for point in obj['track']:
            p = PointSource(point[0], point[1])
            p.setZ(point[2])
            object.track.addPoint(p)

        return object


    @staticmethod
    def saveObjects(list_of_objects: list, way_to_file: str):
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
                obj_dictionary = SaveLoader.code_dispatcher(obj)

            elif (isinstance(obj, (ControlPointSource, StartDeviceSource))):
                obj_dictionary = SaveLoader.code_base(obj)

            elif (isinstance(obj, RadarSource)):
                obj_dictionary = SaveLoader.code_radar(obj)

            elif (isinstance(obj, AeroTargetSource)):
                obj_dictionary = SaveLoader.code_target(obj)

            list_od_dicts.append(obj_dictionary)

        with open(way_to_file, 'w') as outfile:
            json.dump(list_od_dicts, outfile)
        return 0

    @staticmethod
    def uploadObjects(way_to_file: str):
        try:
            with open(way_to_file, 'r') as file:
                objects = json.load(file)

            uploaded_objects = []
            for obj in objects:
                if SaveLoader.parse_type(obj):
                    if obj['type'] == 'DispatcherSource':
                        uploaded_objects.append(SaveLoader.parse_dispatcher(obj))
                    elif obj['type'] == 'ControlPointSource':
                        uploaded_objects.append(SaveLoader.parse_base(obj, 'ControlPointSource'))
                    elif obj['type'] == 'StartDeviceSource':
                        uploaded_objects.append(SaveLoader.parse_base(obj, 'StartDeviceSource'))
                    elif obj['type'] == 'RadarSource':
                        uploaded_objects.append(SaveLoader.parse_radar(obj))
                    elif obj['type'] == 'AeroTargetSource':
                        uploaded_objects.append(SaveLoader.parse_target(obj))

            return uploaded_objects
        except FileNotFoundError:
            print("Данного файла не существует.")
            return []
        except Exception:
            print("Невозможно загрузить данный файл.")
            return []
