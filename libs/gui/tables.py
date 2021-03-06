from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

from libs import pygeoip
from libs.language import Translate
from libs.gui.filters import initFilters

# Multi Lang
translate = Translate()
_ = lambda _word: translate.word(_word)

# Initial geo ip database
geo_ip_database = pygeoip.GeoIP(os.path.join('assets', 'GeoIP.dat'))

class updateClientsTable:

    def __init__(self, moderat):

        self.moderat = moderat
        self.assets = self.moderat.assets
        self.flags = os.path.join(self.assets, 'flags')

        self.item_style = '''
        padding: 2px;
        color: #cff7f8;
        font: 75 10px "MS Shell Dlg 2";
        border: 3px solid;
        border-right: none;
        border-top: none;
        border-bottom: none;
        border-color: #34495e;
        '''

        self.filter = initFilters(self.moderat, self.assets)

    def clean_tables(self):
        self.moderat.clientsTable.setRowCount(1)
        self.moderat.offlineClientsTable.setRowCount(1)
        self.moderat.moderatorsTable.setRowCount(1)

    def update_clients(self, data):
        clients = data['payload']
        online_clients = {}
        offline_clients = {}

        filters = self.filter.filters
        offline_filters = self.filter.offline_filters

        # Filter Clients
        for index, key in enumerate(clients):
            if clients[key]['status']:
                if filters['moderator'] in clients[key]['moderator'] and \
                                filters['ip_address'] in clients[key]['ip_address'] and \
                                filters['alias'] in clients[key]['alias'] and \
                                filters['key'] in str(clients[key]['key']) and \
                                filters['os'] in clients[key]['os'] and \
                                filters['user'] in clients[key]['user'] and \
                                filters['privs'] in clients[key]['privileges'] and \
                                filters['audio'] in clients[key]['audio_device'] and \
                                filters['camera'] in clients[key]['webcamera_device'] and \
                                filters['title'] in clients[key]['window_title']:
                    online_clients[index] = clients[key]
            else:
                if offline_filters['moderator'] in clients[key]['moderator'] and \
                                offline_filters['key'] in clients[key]['key'] and \
                                offline_filters['alias'] in clients[key]['alias'] and \
                                offline_filters['ip_address'] in clients[key]['ip_address']:
                    offline_clients[index] = clients[key]

        # Arange Clients Table
        self.moderat.clientsTable.setRowCount(len(online_clients) + 1)

        for index, obj in enumerate(online_clients):

            # add moderator
            item = QTableWidgetItem(online_clients[obj]['moderator'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setTextColor(QColor('#f1c40f'))
            self.moderat.clientsTable.setItem(index + 1, 0, item)

            # add ip address & county flag
            ip_address = online_clients[obj]['ip_address']
            item = QTableWidgetItem(ip_address)
            item.setIcon(QIcon(self.get_ip_location(ip_address)))
            self.moderat.clientsTable.setItem(index + 1, 1, item)

            # add alias if avaiable
            alias = online_clients[obj]['alias']
            item = QTableWidgetItem(alias)
            self.moderat.clientsTable.setItem(index + 1, 2, item)

            # add socket number
            socket_value = str(online_clients[obj]['key'])
            item = QTableWidgetItem(socket_value)
            if socket_value == 'OFFLINE':
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.moderat.clientsTable.setItem(index + 1, 3, item)

            # add os version
            item = QTableWidgetItem(online_clients[obj]['os'])
            item.setIcon(QIcon(os.path.join(self.assets, 'windows.png')))
            self.moderat.clientsTable.setItem(index + 1, 4, item)

            # add server user
            item = QTableWidgetItem(online_clients[obj]['user'])
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.moderat.clientsTable.setItem(index + 1, 5, item)

            # add user privileges
            try:
                privs_status = _('INFO_USER') if not online_clients[obj]['privileges'] == '1' else _(
                    'INFO_ADMIN')
            except KeyError:
                pass
            item = QTableWidgetItem()
            if privs_status == _('INFO_ADMIN'):
                item.setIcon(QIcon(os.path.join(self.assets, 'admin.png')))
            else:
                item.setIcon(QIcon(os.path.join(self.assets, 'user.png')))
            item.setText(privs_status)
            self.moderat.clientsTable.setItem(index + 1, 6, item)

            # add input device
            item = QTableWidgetItem()
            if online_clients[obj]['audio_device'] == 'NoDevice':
                item.setIcon(QIcon(os.path.join(self.assets, 'mic_no.png')))
                item.setText(_('INFO_NO'))
            else:
                item.setIcon(QIcon(os.path.join(self.assets, 'mic_yes.png')))
                item.setText(_('INFO_YES'))
            self.moderat.clientsTable.setItem(index + 1, 7, item)

            # add webcam device
            item = QTableWidgetItem()
            if online_clients[obj]['webcamera_device'] == 'NoDevice':
                item.setIcon(QIcon(os.path.join(self.assets, 'web_camera_no.png')))
                item.setText(_('INFO_NO'))
            else:
                item.setIcon(QIcon(os.path.join(self.assets, 'web_camera.png')))
                item.setText(_('INFO_YES'))
            self.moderat.clientsTable.setItem(index + 1, 8, item)

            # add active windows title
            item = QTableWidgetItem(online_clients[obj]['window_title'])
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setTextColor(QColor('#1abc9c'))
            self.moderat.clientsTable.setItem(index + 1, 9, item)

        self.moderat.offlineClientsTable.setRowCount(len(offline_clients) + 1)
        try:
            for index, obj in enumerate(offline_clients):
                item = QTableWidgetItem(offline_clients[obj]['moderator'])
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setTextColor(QColor('#f1c40f'))
                self.moderat.offlineClientsTable.setItem(index + 1, 0, item)

                item = QTableWidgetItem(offline_clients[obj]['key'])
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.moderat.offlineClientsTable.setItem(index + 1, 1, item)

                item = QTableWidgetItem(offline_clients[obj]['alias'])
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.moderat.offlineClientsTable.setItem(index + 1, 2, item)

                item = QTableWidgetItem(offline_clients[obj]['ip_address'])
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.moderat.offlineClientsTable.setItem(index + 1, 3, item)

                item = QTableWidgetItem(offline_clients[obj]['last_online'])
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.moderat.offlineClientsTable.setItem(index + 1, 4, item)

        except RuntimeError:
            pass

    def update_moderators(self, data):
        moderators = data['payload']
        self.moderat.moderatorsTable.setRowCount(len(moderators))

        for index, key in enumerate(moderators):

            # add moderator id
            item = QTableWidgetItem(key)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 0, item)

            # add online clients count
            item = QTableWidgetItem(str(moderators[key]['online_clients']))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 1, item)

            # add offline clients count
            item = QTableWidgetItem(str(moderators[key]['offline_clients']))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 2, item)

            # add privileges
            privileges = moderators[key]['privileges']
            if privileges == 1:
                color = '#9b59b6'
                privileges = _('MODERATORS_PRIVILEGES_ADMINISTRATOR')
            else:
                color = '#c9f5f7'
                privileges = _('MODERATORS_PRIVILEGES_MODERATOR')
            item = QTableWidgetItem(privileges)
            item.setTextColor(QColor(color))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 3, item)

            # add moderator status
            status = moderators[key]['status']
            if status == 1:
                style = '#1abc9c'
                text = _('MODERATOR_ONLINE')
            else:
                style = '#e67e22'
                text = _('MODERATOR_OFFLINE')
            item = QTableWidgetItem(text)
            item.setTextColor(QColor(style))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 4, item)

            # add moderator last online
            item = QTableWidgetItem(str(moderators[key]['last_online']))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.moderat.moderatorsTable.setItem(index, 5, item)

    def get_ip_location(self, ip):
        try:
            country_flag = os.path.join(self.flags, geo_ip_database.country_code_by_addr(ip).lower() + '.png')
            if os.path.exists(country_flag):
                return country_flag
            else:
                return os.path.join(self.flags, 'blank.png')
        except:
            return os.path.join(self.flags, 'blank.png')