# GuideMissile constants
GuidedMissile_SPEED = 1200  # скорость ЗУР, в м/с 1200
GuidedMissile_LifeTime = 36000  # максмальное время жизни ЗУР, в секундах
GuidedMissile_ExplRadius = 100  # поражающих осколков ЗУР, в метрах
GuidedMissile_MaxRotAngle = 0.79  # максимальный угол, на который может повернуть ракета при каждом шаге, в радианах

Airplane_SPEED = 555  # скорость самолета в м/c 555
Airplane_MaxRotAngle = 0.79  # максимальный угол, на который может повернуть самолет при каждом шаге, в радианах
Airplane_SIZE = 20  # характерный размер самолета
Airplane_DistUpdate = 100  # расстояние до контрольной точки, при которой она считается достигнутой
EPS = 1e-7  # слагаемое, чтобы избежать деление на 0

NUMBER_OF_MISSILES = 10

DISPATCHER_ID = 0
DRAWER_ID = -1000
DISPATCHER_ID = 0

MISSILE_TYPE_DRAWER = 0
TARGET_TYPE_DRAWER = 1
OLD_GM = 2
OLD_TARGET = 1
NEW_TARGET = 0
# messages_classes

MSG_RADAR2CCP_type = 2001
MSG_RADAR2GM_type = 2002
MSG_RADAR2CCP_GM_HIT_type = 2003

MSG_CCP2SD_type = 3001
MSG_CCP2GM_type = 3002
MSG_CCP2RADAR_type = 3003
MSG_CCP_MISSILE_CAPACITY_type = 3004

MSG_GM2RADAR_type = 4001

MSG_SD2CCP_MS_type = 6001
MSG_SD2CCP_NS_type = 6002

MSG_RADAR2DRAWER_type = -1
MSG_CCP2GUItype = -2

MSG_AEROENV2DISPATCHER_type = 7001
MSG_AEROENV2DISPATCHER_VIEW_type = 7002




