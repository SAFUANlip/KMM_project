# константы ЗУР
GuidedMissile_SPEED = 1200  # скорость ЗУР по дефолту, в м/с 1200
GuidedMissile_SPEED_MAX = 2200  # верхняя граница скорости ЗУР
GuidedMissile_SPEED_MIN = 1100  # нижняя граница скорости ЗУР
GuidedMissile_LifeTime = 400  # максмальное время жизни ЗУР, в секундах
GuidedMissile_ExplRadius = 100  # поражающих радиус осколков ЗУР, в метрах
GuidedMissile_MaxRotAngle = 0.79  # максимальный угол, на который может повернуть ракета при каждом шаге, в радианах 45град
GuidedMissile_SIZE = 2.0  # характерный размер ракеты в метрах
GuidedMissile_ExplRadiusError = 60  # допустимая ошибка определения расстояния до цели, при проверке взрыва

# константы самолета
Airplane_SPEED = 555  # скорость самолета в м/c 555
Airplane_SPEED_MAX = 700  # верхняя граница для скорости самолета
Airplane_SPEED_MIN = 220  # нижняя граница для скорости самолета
Airplane_MaxRotAngle = 0.79  # максимальный угол, на который может повернуть самолет при каждом шаге, в радианах 45град
Airplane_SIZE = 20.0  # характерный размер самолета
Airplane_DistUpdate = 100  # расстояние до контрольной точки, при которой она считается достигнутой

# константы Радара
MAX_ERROR_DIST = 50  # максимальная ошибка определения дальности до объекта, м
RATE_ERROR_SPEED = 5e-4  # относительная ошибка измерения траекторной скорости
MIN_DIST_DETECTION = 30  # минимальное расстояние, на котором РЛС видит объект, м

EPS = 1e-7  # слагаемое, чтобы избежать деление на 0

# константы Радара
RATE_ERROR_DIST = 0.05
RATE_ERROR_SPEED = 0.001
MIN_DIST_DETECTION = 30  # м
MAX_DIST_DETECTION = 50000 # м
NUMBER_OF_MISSILES = 10

DISPATCHER_ID = 0
DRAWER_ID = -1000

MISSILE_TYPE_DRAWER = 0
TARGET_TYPE_DRAWER = 1
OLD_GM = 2
OLD_TARGET = 1
NEW_TARGET = 0

# классы сообщений
MSG_RADAR2CCP_type = 2001
MSG_RADAR2GM_type = 2002
MSG_RADAR2CCP_GM_HIT_type = 2003
MSG_RADAR2DISPATCHER_INIT_type = 2004
MSG_RADAR2DISPATCHER_VIEW_type = 2005
MSG_RADAR2DRAWER_type = -1

MSG_CCP2SD_type = 3001
MSG_CCP2GM_type = 3002
MSG_CCP2RADAR_type = 3003
MSG_CCP_MISSILE_CAPACITY_type = 3004
MSG_CCP2DISPATCHER_VIEW_type = 3005
MSG_CCP2DISPATCHER_INIT_type = 3006
MSG_CCP2DRAWER_type = 3007
MSG_CCP2GUItype = -2

MSG_GM2RADAR_type = 4001

MSG_SD2CCP_MS_type = 6001
MSG_SD2CCP_NS_type = 6002

MSG_AEROENV2DISPATCHER_type = 7001
MSG_AEROENV2DISPATCHER_VIEW_type = 7002


# ограничения на положения объектов и сетку
env_limits = {
    'X: м': [-100000, 100000],
    'Y: м': [-100000, 100000],
    'Z: м': [0, 20000],
}

# ограничение на максимальное и минимальное время моделирования в секундах
min_model_time = 60
max_model_time = 500

ccp_rad = 10  # Радиус, в котром ПБУ проверяет возможное положение целей




