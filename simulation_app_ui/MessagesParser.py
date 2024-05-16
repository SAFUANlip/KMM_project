import numpy as np

from simulation_process.messages_classes.Messages import (CombatControlPoint_InitMessage,
                                                          CombatControlPoint_ViewMessage,
                                                          AeroEnv_InitMessage,
                                                          AeroEnv_ViewMessage,
                                                          Radar_InitMessage,
                                                          Radar_ViewMessage)


def parse_messages(all_messages):
    objs = {
        "vo": [],
        "controls": [],
        "radars": [],
    }
    trajs = {
        "vo": {},
        "radars": {},
        "controls": {},
        "max_time": 0
    }
    mixed_messages = []
    for el in all_messages:
        mixed_messages += el

    # AeroEnv messages

    env_view_messages = []
    for el in mixed_messages:
        if isinstance(el, AeroEnv_ViewMessage):
            env_view_messages.append(el)
        elif isinstance(el, AeroEnv_InitMessage):
            objs["vo"].append(el.sender_ID)

    trajs["vo"], trajs["max_time"] = parse_env_trajectories(env_view_messages)

    print("Parsed VO views")

    # Controls messages
    cc_view_messages = []
    for el in mixed_messages:
        if isinstance(el, CombatControlPoint_ViewMessage):
            cc_view_messages.append(el)
        elif isinstance(el, CombatControlPoint_InitMessage):
            objs["controls"].append(el.sender_ID)

    for control_id in objs["controls"]:
        trajs["controls"][control_id] = parse_control_trajectories(control_id, cc_view_messages)

    print("Parsed control views")

    # Radars messages
    # Controls messages
    radar_view_messages = []
    for el in mixed_messages:
        if isinstance(el, Radar_ViewMessage):
            radar_view_messages.append(el)
        elif isinstance(el, Radar_InitMessage):
            objs["radars"].append(el.sender_ID)

    for control_id in objs["radars"]:
        trajs["radars"][control_id] = parse_radar_trajectories(control_id, radar_view_messages)

    print("Parsed radar views")

    return objs, trajs


def parse_control_trajectories(control_id, messages):
    control_messages = []
    for msg in messages:
        if msg.sender_ID == control_id:
            control_messages.append(msg)

    control_messages.sort(key=lambda c_msg: c_msg.time)
    objects = {
        "targets": [],
        "missiles": {}
    }

    for msg in control_messages:
        keys = ["targets", "missiles"]
        for pair_id_pos in msg.view_dict["missiles"]:
            obj_id = pair_id_pos[1]
            obj_pos = pair_id_pos[2]
            obj_pos = list(obj_pos) + [msg.time]
            if obj_id in objects["missiles"]:
                objects["missiles"][obj_id].append(obj_pos)
            else:
                objects["missiles"][obj_id] = [obj_pos]

        for pair_time_pos in msg.view_dict["targets"]:
            obj_time = pair_time_pos[0]
            obj_pos = pair_time_pos[1]
            obj_pos = list(obj_pos) + [msg.time]
            objects["targets"].append(obj_pos)

    return objects


def parse_radar_trajectories(radar_id, messages):
    radar_messages = []
    for msg in messages:
        if msg.sender_ID == radar_id:
            radar_messages.append(msg)


    radar_messages.sort(key=lambda c_msg: c_msg.time)
    objects = {
        "targets": [],
        "missiles": {}
    }

    for msg in radar_messages:
        for pos in msg.pos_objects:
            # obj_id - None
            position_and_time = list(pos) + [msg.time]
            objects["targets"].append(position_and_time)
    return objects


def parse_env_trajectories(messages):

    messages.sort(key=lambda c_msg: c_msg.time)
    objects = {
        "targets": {},
        "missiles": {}
    }
    if len(messages) == 0:
        return objects, 0

    max_time = messages[-1].time
    for msg in messages:
        time_stamp = msg.time
        keys = ["targets", "missiles"]
        for key in keys:
            for pair_id_pos in msg.view_dict[key]:
                obj_id = pair_id_pos[0]
                # position and time
                obj_pos = list(pair_id_pos[1]) + [time_stamp]
                if obj_id in objects[key]:
                    objects[key][obj_id].append(obj_pos)
                else:
                    objects[key][obj_id] = [obj_pos]

    return objects, max_time


def fake_parse_messages(all_messages):
    objs = {"radars": [1, 2, 3], "controls": [1, 2], "vo": [0], }
    trajs = {
        "radars": {1:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([30, 30])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                   2:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                   3:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]}
                   },
        "controls": {1:
                         {259: [np.array([10, 10]), np.array([20, 20]), np.array([30, 30])],
                          260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                     2:
                         {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                          260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]}
                     },
        "vo": {
            "targets":
                {259: [np.array([20000, 20000]), np.array([20000, 6000]), np.array([30, 30])],
                 260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
            "missiles": {}
        },
    }
    return objs, trajs
