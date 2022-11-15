# imported packages

import re
import smtplib
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import csv
import os
from bokeh.models import BoxAnnotation
import paramiko
import time
from bokeh.plotting import figure, output_file, show, save
from math import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.transform import cumsum
from bokeh.transform import factor_cmap
from bokeh.models import LabelSet, ColumnDataSource
from bokeh.models import HoverTool
from netmiko import ConnectHandler
from bokeh.io import output_file, show
from bokeh.palettes import Spectral6, Dark2
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.models import TabPanel, Tabs
from bokeh.transform import dodge

# reference

# ['show process cpu', 'show version', 'show platform temperature', 'date',
# 'show system memory', 'show processes memory', 'show interface counters', 'show processes summary', 'docker_stats']


# initialising variable globally
month = {'Jan': '01', 'Feb': '02', 'Mar': '03', "Apr": '04', "May": '05', "Jun": '06', "Jul": '07', "Aug": '08',
         "Sep": '09', "Oct": '10', "Nov": '11', "Dec": '12'}
line_counter = [0, 0, 0, 0, 0, 0, 0, 0, 0]
command_running = [False, False, False, False, False, False, False, False, False]
sep_line = '-----------------------------------------------------------------------------\n\n'
overall_alert_temp = []
overall_alert_cpu = []
date = []
cpu_graph = []
temp_graph = []
temp_sensor_names = []
memory_graph = []
docker_stats_graph = []
docker_stats_sensor_names = []
counters_names = []
counters = []


def main(command, ip_address, username, password, snapshot_count):
    # initialised variable
    try:
        combined_result = ''
        # traversing in list path
        # session=paramiko.SSHClient()
        # session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # session.connect(ip_address,username=username,password=password)
        linux = {
            'device_type': 'linux',
            'ip': ip_address,
            'username': username,
            'password': password,
        }
        connection = ConnectHandler(**linux)
        for number in range(0, snapshot_count):

            # initialised variables
            print("Taking snapshot : " + str(number + 1))
            result = '\n\n\n'
            process_taken = False
            cpu_taken = False
            cpu_count = 0
            process_count = 0
            counters_temp = []
            alert_temp = []
            alert_cpu = []
            docker_temp = []
            temp_memory_graph_point = []
            temp_graph_temp = []
            docker_stats_graph_temp = []
            # f = ''
            # for i in command:
            # (stdin, stdout, stderr)=session.exec_command(i+'\n\n')
            # router_output = stdout.read()
            # f = f +'admin@sonic:~$ '+ i+'\n\n'+router_output.decode("utf-8")+'\n'
            f = connection.send_config_set(command)
            result_list = f.split('\n')
            counter = 0
            for x in result_list:
                counter = counter + 1
                # checking which command starts
                process_cpu = re.search('show processes cpu', x)
                version = re.search('show version', x)
                platform_temperature = re.search('show platform temperature', x)
                date_1 = re.search('admin', x)
                date_2 = re.search('date', x)
                system_memory = re.search('show system-memory', x)
                processes_memory = re.search('show processes memory', x)
                interface_counters = re.search('show interface counters', x)
                processes_summary = re.search('show processes summary', x)
                docker_stats = re.search('docker stats  --no-stream', x)

                # to update which command is running
                if process_cpu:
                    update_command(line_counter, command_running, 0)

                if version:
                    update_command(line_counter, command_running, 1)

                if platform_temperature:
                    update_command(line_counter, command_running, 2)

                if date_1 and date_2:
                    update_command(line_counter, command_running, 3)

                if system_memory:
                    update_command(line_counter, command_running, 4)

                if processes_memory:
                    update_command(line_counter, command_running, 5)

                if interface_counters:
                    update_command(line_counter, command_running, 6)

                if processes_summary:
                    update_command(line_counter, command_running, 7)

                if docker_stats:
                    update_command(line_counter, command_running, 8)

                # show process cpu
                if command_running[0]:
                    index = 0
                    ans = show_process_cpu(index, cpu_taken, cpu_count, x)
                    result += ans[0]
                    cpu_taken = ans[1]
                    cpu_count = ans[2]
                    if ans[3] != '-1':
                        alert_cpu.append(x)

                # show version
                if command_running[1]:
                    index = 1
                    result += show_version(index, x)

                # show platform temperature
                if command_running[2]:
                    index = 2
                    ans = show_platform_temperature(index, x)
                    result += ans[0]
                    if ans[1] != '-1':
                        alert_temp.append(x)
                    if ans[2] != '-1':
                        lst = x.split()
                        if len(lst) >= 9:
                            if len(temp_graph) == 0:
                                temp_sensor_names.append(lst[0])
                            temp_graph_temp.append(float(lst[1]))

                # date
                if command_running[3]:
                    index = 3
                    ans = show_date(index, x)
                    result += ans[0]
                    if ans[1] != '-1':
                        date.append(ans[1])

                # show system memory
                if command_running[4]:
                    index = 4
                    a = re.search('Mem:', x)
                    if a:
                        lst = x.split()
                        temp_memory_graph_point.append(int(lst[1]))
                        temp_memory_graph_point.append(int(lst[2]))
                        temp_memory_graph_point.append(int(lst[3]))
                    result += show_system_memory(index, x)

                # show processes memory
                if command_running[5]:
                    index = 5
                    ans = show_processes_memory(index, process_taken, process_count, x)
                    result += ans[0]
                    process_taken = ans[1]
                    process_count = ans[2]

                # show interface counters
                if command_running[6]:
                    index = 6
                    result += show_interface_counters(counters_temp, index, x)



                if command_running[7]:
                    pass

                # docker stats
                if command_running[8]:
                    index = 8
                    ans = show_docker_stats(index, x)
                    result += ans[0]
                    if ans[1] != '-1':
                        lst = x.split()
                        if len(lst) == 14:
                            if len(docker_stats_graph) == 0:
                                docker_stats_sensor_names.append(lst[1])
                            docker_stats_graph_temp.append(float(lst[2][:-1]))

            docker_stats_graph.append(docker_stats_graph_temp)
            combined_result += '\n\n\n######################################################################\n\n'
            combined_result += 'from snapshot ' + str(number + 1) + ' ----> ' + str(number) + '\n\n'
            combined_result += '######################################################################'
            combined_result += result
            temp_graph.append(temp_graph_temp)
            memory_graph.append(temp_memory_graph_point)
            overall_alert_cpu.append(alert_cpu)
            overall_alert_temp.append(alert_temp)
            counters.append(counters_temp)

        # alert
        # alert(overall_alert_temp, overall_alert_cpu)
        # print(counters)
        for i in range(0, len(counters[0])):
            counters_names.append(counters[0][i][0])
        # print(counters_names)
        plot_cpu(cpu_graph, date)
        plot_temp(temp_graph, temp_sensor_names, date)
        plot_memory(memory_graph, date)
        plot_docker(docker_stats_graph, docker_stats_sensor_names, cpu_graph, date)
        to_csv(temp_graph, temp_sensor_names, cpu_graph, memory_graph, date, docker_stats_graph,
               docker_stats_sensor_names)
        final_result = '\n\n########################################################################## \n\n'
        final_result += min_max_average(temp_graph, temp_sensor_names, cpu_graph, memory_graph, docker_stats_graph,
                                        docker_stats_sensor_names)
        final_result += combined_result
        text_file(final_result)

        # Closing the connection
        # session.close()
        connection.disconnect()

    except:
        # print(exception)
        print(
            "* Invalid username or password :( \n* Please check the username/password file or the device configuration.")
        print("* Closing program... Bye!")


# average
def average(lst):
    sum_of_list = 0
    for i in range(0, len(lst)):
        sum_of_list += lst[i]
    avg = sum_of_list / len(lst)
    return avg


# minimum maximum average
def min_max_average(temp_graph, temp_sensor_names, cpu_graph, memory_graph, docker_stats_graph,
                    docker_stats_sensor_names):
    result = ''
    # cpu data
    result += 'CPU usage data' + '\n'
    result += 'minimum CPU usage ' + str(min(cpu_graph)) + '\n'
    result += 'maximum CPU usage ' + str(max(cpu_graph)) + '\n'
    result += 'average CPU usage ' + str(average(cpu_graph)) + '\n\n'

    # temperature data

    result += "Temperature data\n"
    for i in range(0, len(temp_sensor_names)):
        temporary = []
        for j in range(0, len(temp_graph)):
            temporary.append(temp_graph[j][i])

        result += temp_sensor_names[i] + ' Temperature data' + '\n'
        result += 'minimum' + temp_sensor_names[i] + ' temperature ' + str(min(temporary)) + '\n'
        result += 'maximum' + temp_sensor_names[i] + ' temperature ' + str(max(temporary)) + '\n'
        result += 'average' + temp_sensor_names[i] + ' temperature ' + str(round(average(temporary), 3)) + '\n\n'

    # memory data
    total_list = []
    used_list = []
    free_list = []
    other_list = []
    for i in range(0, len(memory_graph)):
        total_list.append(memory_graph[i][0])
        used_list.append(memory_graph[i][1])
        free_list.append(memory_graph[i][2])
        other_list.append(memory_graph[i][0] - memory_graph[i][1] - memory_graph[i][2])

    result += 'memory data' + '\n'
    result += 'Total ---> Minimum ' + str(min(total_list)) + ' Maximum ' + str(max(total_list)) + ' Average ' + str(
        round(average(total_list), 3)) + '\n'
    result += 'Used  ---> Minimum ' + str(min(used_list)) + ' Maximum ' + str(max(used_list)) + ' Average ' + str(
        round(average(used_list), 3)) + '\n'
    result += 'Free  ---> Minimum ' + str(min(free_list)) + ' Maximum ' + str(max(free_list)) + ' Average ' + str(
        round(average(free_list), 3)) + '\n'
    result += 'Other ---> Minimum ' + str(min(other_list)) + ' Maximum ' + str(max(other_list)) + ' Average ' + str(
        round(average(other_list), 3)) + '\n\n'

    # docker stats data
    result += 'docker stats data' + '\n'
    for i in range(0, len(docker_stats_graph[0])):
        temporary = []
        for j in range(0, len(docker_stats_graph)):
            temporary.append(docker_stats_graph[j][i])
        result += docker_stats_sensor_names[i] + '   ---> Minimum ' + str(min(temporary)) + ' Maximum ' + str(
            max(temporary)) + ' Average ' + str(
            round(average(temporary), 3)) + '\n'
    return result


# create csv files
def to_csv(temp_graph, temp_sensor_names, cpu_graph, memory_graph, date, docker_stats_graph, docker_stats_sensor_names):
    # to convert date string to datetime object
    date_ = []
    for i in date:
        lst = i.split()
        str = ''
        str += month[lst[2]]
        str += '/'
        str += lst[1]
        str += '/'
        str += lst[3][2:]
        datetime_str = str + " " + lst[4]
        # datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        date_.append(i)

    # store temp_graph data
    temp_list = []
    # store docker_graph data
    docker_list = []
    # store cpu_usage data
    cpu_list = []
    # store memory_usage data
    memory_list = []
    for i in range(0, len(temp_graph)):
        temporary = []
        for j in range(0, len(temp_graph[0])):
            temporary.append(temp_graph[i][j])
        temporary.append(date_[i])
        temp_list.append(temporary)
    for i in range(0, len(date)):
        cpu_list.append([cpu_graph[i], date_[i]])
    for i in range(0, len(docker_stats_graph)):
        temporary = []
        for j in range(0, len(docker_stats_graph[0])):
            temporary.append(docker_stats_graph[i][j])
        temporary.append(cpu_graph[i])
        temporary.append(date_[i])
        docker_list.append(temporary)

    for i in range(0, len(date)):
        memory_list.append([date_[i], memory_graph[i][0], memory_graph[i][1], memory_graph[i][2],
                            memory_graph[i][0] - memory_graph[i][1] - memory_graph[i][2]])

    # header of temperature
    header_temp = []
    for i in temp_sensor_names:
        header_temp.append(i)
    header_temp.append('Time')
    # header of cpu_usage
    header_cpu = ['CPU usage percentage', 'Time']
    # header of memory_usage
    header_memory = ['Time', 'Total', 'Used', 'Free', 'Other']
    # header of docker stats
    header_docker = docker_stats_sensor_names
    header_docker.append('System CPU%')
    header_docker.append('Time')

    # make directory for showing output
    CURR_DIR = os.getcwd()
    if not os.path.exists(CURR_DIR + '\output'):
        os.mkdir(CURR_DIR + '\output', mode=0o666)
    if not os.path.exists(CURR_DIR + '\output\csv'):
        os.mkdir(CURR_DIR + '\output\csv', mode=0o666)

    # creating and storing data in temp_graph_PSU1.csv
    f1 = open(CURR_DIR + '/output/csv/temp_graph.csv', 'w')
    writer = csv.writer(f1)
    writer.writerow(header_temp)
    writer.writerows(temp_list)

    # creating and storing data in cpu_usage.csv
    f2 = open(CURR_DIR + '/output/csv/cpu_usage.csv', 'w')
    writer = csv.writer(f2)
    writer.writerow(header_cpu)
    writer.writerows(cpu_list)

    # creating and storing data in memory_usage.csv
    f3 = open(CURR_DIR + '/output/csv/memory_usage.csv', 'w')
    writer = csv.writer(f3)
    writer.writerow(header_memory)
    writer.writerows(memory_list)

    # creating and storing data in memory_usage.csv
    f4 = open(CURR_DIR + '/output/csv/docker_stats.csv', 'w')
    writer = csv.writer(f4)
    writer.writerow(header_docker)
    writer.writerows(docker_list)


# creating result.txt
def text_file(combined_result):
    f = open("result.txt", "w+")
    f.write(combined_result)
    f.close()


# plotting docker stats graph
def plot_docker(docker_stats_graph, docker_stats_sensor_names, cpu_graph, date):
    CURR_DIR = os.getcwd()
    time = []
    for i in date:
        lst = i.split()
        str = ''
        str += month[lst[2]]
        str += '/'
        str += lst[1]
        str += '/'
        str += lst[3][2:]
        datetime_str = str + " " + lst[4]
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        time.append(datetime_object)
    if not os.path.exists(CURR_DIR + '\output'):
        os.mkdir(CURR_DIR + '\output', mode=0o666)
    if not os.path.exists(CURR_DIR + '\output\graphs'):
        os.mkdir(CURR_DIR + '\output\graphs', mode=0o666)
    output_file(CURR_DIR + '/output/graphs/docker_graphs.html')
    name_list = []
    items = ['docker%', 'cpu%']
    for i in range(0, len(docker_stats_graph[0])):
        temp = []
        date_ = []
        none = []

        for j in date:
            lst = j.split()
            date_.append(lst[4])

        for j in range(0, len(docker_stats_graph)):
            temp.append(docker_stats_graph[j][i])
            none.append(0)

        data = {'date': date_,
                'cpu%': cpu_graph,
                'docker%': temp,
                'none': none,
                'time': time
                }
        low_box = BoxAnnotation(bottom=0, top=10, fill_alpha=0.1, fill_color='green')
        high_box = BoxAnnotation(bottom=10, fill_alpha=0.1, fill_color='red')

        source = ColumnDataSource(data=data)

        name_bar = figure(x_range=date_, title=docker_stats_sensor_names[i],
                          toolbar_location=None, tools="", x_axis_label='Date Time', y_axis_label='CPU %')

        name_bar.vbar(x=dodge('date', -0.25, range=name_bar.x_range), top='cpu%', width=0.2, source=source,
                      color="#FF0000", legend_label="cpu%", name='cpu%')

        name_bar.vbar(x=dodge('date', 0.0, range=name_bar.x_range), top='docker%', width=0.2, source=source,
                      color="#32CD32", legend_label="docker%", name='docker%')

        hover = HoverTool()
        hover.tooltips = """
        <div>
            <div><strong>Time : </strong>@date</div>
            <div><strong>Value : </strong>@$name</div>
        </div>"""
        name_bar.add_tools(hover)
        name_bar.x_range.range_padding = 0.1
        name_bar.xgrid.grid_line_color = None
        name_bar.legend.location = "top_left"
        name_bar.legend.orientation = "horizontal"
        name_bar.xaxis.major_label_orientation = "vertical"
        name_bar.add_layout(low_box)
        name_bar.add_layout(high_box)
        tab2 = TabPanel(child=name_bar, title="bar")

        name_line = 'p_line' + "% s" % i
        hover = HoverTool(tooltips=[('value', '@$name'), ('time', '@date')])
        name_line = figure(title=docker_stats_sensor_names[i], x_axis_label='Date Time', y_axis_label='Percentage change',
                           x_axis_type='datetime', tools=[hover])
        name_line.line(x='time', y='cpu%', source=data, legend_label="CPU %", line_width=2, name='cpu%',
                       color='#FF0000')
        name_line.line(x='time', y='docker%', source=data, legend_label="DOCKER %", line_width=2, name='docker%',
                       color="#32CD32")
        name_line.add_layout(low_box)
        name_line.add_layout(high_box)
        tab1 = TabPanel(child=name_line, title="line")

        name_circle = 'p_circle' + "% s" % i
        hover = HoverTool(tooltips=[('value', '@$name'), ('time', '@date')])
        name_circle = figure(title=docker_stats_sensor_names[i], x_axis_label='Date Time', y_axis_label='percentage change',
                             x_axis_type='datetime', tools=[hover])
        name_circle.circle(x='time', y='cpu%', source=data, legend_label="CPU %", line_width=2, name='cpu%',
                           color='#FF0000')
        name_circle.circle(x='time', y='docker%', source=data, legend_label="DOCKER %", line_width=2, name='docker%',
                           color="#32CD32")
        name_circle.add_layout(low_box)
        name_circle.add_layout(high_box)
        tab3 = TabPanel(child=name_circle, title="circle")

        tabs = Tabs(tabs=[tab2, tab1, tab3])
        name_list.append(tabs)

    save(name_list)


# plotting memory graphs
def plot_memory(memory_graph, date):
    # saving file
    CURR_DIR = os.getcwd()
    if not os.path.exists(CURR_DIR + '\output'):
        os.mkdir(CURR_DIR + '\output', mode=0o666)
    if not os.path.exists(CURR_DIR + '\output\graphs'):
        os.mkdir(CURR_DIR + '\output\graphs', mode=0o666)
    output_file(CURR_DIR + '/output/graphs/memory_graphs.html')
    name_list = []
    # memory data
    total_list = []
    used_list = []
    free_list = []
    other_list = []
    for i in range(0, len(memory_graph)):
        total_list.append(memory_graph[i][0])
        used_list.append(memory_graph[i][1])
        free_list.append(memory_graph[i][2])
        other_list.append(memory_graph[i][0] - memory_graph[i][1] - memory_graph[i][2])
    colors = ['coral', 'yellowgreen', 'aqua']
    # plotting the pie chart
    name = 'p' + str(0)
    x = {
        'used': average(used_list),
        'free': average(free_list),
        'other': average(other_list),
    }

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'memory'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = colors[:len(x)]
    name = figure(height=350, title="Average Memory plot", tools="hover", tooltips="@memory: @value",
                  x_range=(-0.5, 1.0))
    name.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
               line_color="white", fill_color='color', legend_field='memory', source=data)
    name.axis.axis_label = None
    name.axis.visible = False
    name.grid.grid_line_color = None
    name_list.append(name)
    for i in range(0, len(memory_graph)):
        colors = ['coral', 'yellowgreen', 'aqua']
        # plotting the pie chart
        name = 'p' + str(i + 1)
        x = {
            'used': memory_graph[i][1],
            'free': memory_graph[i][2],
            'other': memory_graph[i][0] - memory_graph[i][1] - memory_graph[i][2],
        }

        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'memory'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = colors[:len(x)]
        name = figure(height=350, title="Memory plot at " + str(date[i]), tools="hover", tooltips="@memory: @value",
                      x_range=(-0.5, 1.0))
        name.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                   line_color="white", fill_color='color', legend_field='memory', source=data)
        name.axis.axis_label = None
        name.axis.visible = False
        name.grid.grid_line_color = None
        name_list.append(name)
    save(name_list)


# plotting temperature graph
def plot_temp(temp_graph, temp_sensor_names, date):
    date_ = []
    # saving file
    CURR_DIR = os.getcwd()
    if not os.path.exists(CURR_DIR + '\output'):
        os.mkdir(CURR_DIR + '\output', mode=0o666)
    if not os.path.exists(CURR_DIR + '\output\graphs'):
        os.mkdir(CURR_DIR + '\output\graphs', mode=0o666)
    output_file(CURR_DIR + '/output/graphs/temperature_graphs.html')
    time = []
    for i in date:
        lst = i.split()
        str = ''
        str += month[lst[2]]
        str += '/'
        str += lst[1]
        str += '/'
        str += lst[3][2:]
        datetime_str = str + " " + lst[4]
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        date_.append(datetime_object)
        time.append(lst[4])
    name_list = []
    for i in range(0, len(temp_sensor_names)):
        temporary = []
        for j in range(0, len(temp_graph)):
            temporary.append(temp_graph[j][i])
        from bokeh.models import DatetimeTickFormatter
        data = pd.DataFrame({'date': date_, 'value': temporary, 'time': time})
        low_box = BoxAnnotation(bottom=0, top=35, fill_alpha=0.1, fill_color='green')
        high_box = BoxAnnotation(bottom=35, fill_alpha=0.1, fill_color='red')

        source = ColumnDataSource(data=data)
        hover = HoverTool(tooltips=[('value', '@value'), ('time', '@time')])
        name_line = figure(title="Temperature plot of " + temp_sensor_names[i], x_axis_label='Date Time',
                           y_axis_label='Temperature', x_axis_type='datetime',
                           tools=[hover])
        name_line.line(x='date', y='value', source=data, legend_label="Temperature", line_width=2)
        name_line.add_layout(low_box)
        name_line.add_layout(high_box)
        tab1 = TabPanel(child=name_line, title="line")

        name_circle = figure(title="Temperature plot of " + temp_sensor_names[i], x_axis_label='Date Time', y_axis_label='Temperature', x_axis_type='datetime',
                             tools=[hover])
        name_circle.circle(x='date', y='value', source=data, legend_label="Temperature", line_width=2)
        name_circle.add_layout(low_box)
        name_circle.add_layout(high_box)
        tab2 = TabPanel(child=name_circle, title="circle")

        name_bar = figure(x_range=time, title="Temperature plot of " + temp_sensor_names[i], toolbar_location=None, tools="", x_axis_label='Date Time',
                          y_axis_label='Temperature')
        name_bar.vbar(x='time', top='value', width=0.2, legend_label='Temperature', name='value', source=source)
        name_bar.xgrid.grid_line_color = None
        name_bar.y_range.start = 0
        name_bar.add_tools(HoverTool(tooltips=[("Value", '@$name')]))
        name_bar.xaxis.major_label_orientation = "vertical"
        name_bar.add_layout(low_box)
        name_bar.add_layout(high_box)
        tab3 = TabPanel(child=name_bar, title="bar")
        tabs = Tabs(tabs=[tab1, tab2, tab3])
        name_list.append(tabs)
    if len(name_list) != 0:
        save(name_list)


# plotting cpu usage graph
def plot_cpu(cpu_graph, date):
    # plotting the points
    # saving
    CURR_DIR = os.getcwd()
    if not os.path.exists(CURR_DIR + '\output'):
        os.mkdir(CURR_DIR + '\output', mode=0o666)
    if not os.path.exists(CURR_DIR + '\output\graphs'):
        os.mkdir(CURR_DIR + '\output\graphs', mode=0o666)
    output_file(CURR_DIR + '/output/graphs/cpu_graphs.html')
    date_ = []
    time = []
    for i in date:
        lst = i.split()
        str = ''
        str += month[lst[2]]
        str += '/'
        str += lst[1]
        str += '/'
        str += lst[3][2:]
        datetime_str = str + " " + lst[4]
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        date_.append(datetime_object)
        time.append(lst[4])

    from bokeh.models import DatetimeTickFormatter
    data = pd.DataFrame({'date': date_, 'value': cpu_graph, 'time': time})

    low_box = BoxAnnotation(bottom=0, top=35, fill_alpha=0.1, fill_color='green')
    high_box = BoxAnnotation(bottom=35, fill_alpha=0.1, fill_color='red')

    source = ColumnDataSource(data=data)
    hover = HoverTool(tooltips=[('value', '@value'), ('time', '@time')])
    p1 = figure(title="CPU USAGE", x_axis_label='Date Time', y_axis_label='CPU %', x_axis_type='datetime',
                tools=[hover])
    p1.line(x='date', y='value', source=data, legend_label="CPU %", line_width=2)
    p1.add_layout(low_box)
    p1.add_layout(high_box)
    tab1 = TabPanel(child=p1, title="line")

    p2 = figure(title="CPU USAGE", x_axis_label='Date Time', y_axis_label='CPU %', x_axis_type='datetime',
                tools=[hover])
    p2.circle(x='date', y='value', source=data, legend_label="CPU %", line_width=2)
    p2.add_layout(low_box)
    p2.add_layout(high_box)
    tab2 = TabPanel(child=p2, title="circle")

    p3 = figure(x_range=time, title="CPU USAGE", toolbar_location=None, tools="", x_axis_label='Date Time',
                y_axis_label='CPU %')
    p3.vbar(x='time', top='value', width=0.2, legend_label='CPU %', name='value', source=source)
    p3.xgrid.grid_line_color = None
    p3.y_range.start = 0
    p3.add_tools(HoverTool(tooltips=[("Value", '@$name')]))
    p3.xaxis.major_label_orientation = "vertical"
    p3.add_layout(low_box)
    p3.add_layout(high_box)
    tab3 = TabPanel(child=p3, title="bar")

    tabs = Tabs(tabs=[tab1, tab2, tab3])
    save(tabs)


# alert
def alert(overall_alert_temp, overall_alert_cpu):
    try:
        # Create your SMTP session
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        # Use TLS to add security
        smtp.starttls()

        # User Authentication
        smtp.login("cpuutil@gmail.com", "dciogtkivlexlrrd")

        # Defining The Message

        SUBJECT = 'Warning !!'
        start_temp = False
        start_cpu = False
        text = 'warning and danger !! \n\n\n'
        for i in range(0, len(overall_alert_temp)):
            if len(overall_alert_temp[i]) != 0:
                if not start_temp:
                    start_temp = True
                    text += 'SHOW PLATFORM TEMPERATURE \n\n\n'
                text += '   ' + date[i] + '\n\n'
            for j in range(0, len(overall_alert_temp[i])):
                lst = overall_alert_temp[i][j].split()
                text += '       ' + lst[0] + ' has a temperature of ' + lst[1] + '\n'
            text += '\n\n'
        for i in range(0, len(overall_alert_cpu)):
            if len(overall_alert_cpu[i]) != 0:
                if not start_cpu:
                    start_cpu = True
                    text += 'SHOW PROCESS CPU \n\n\n'
                text += '   ' + date[i] + '\n\n'
            for j in range(0, len(overall_alert_cpu[i])):
                lst = overall_alert_cpu[i][j].split()
                text += '       ' + lst[11] + ' has a CPU temperature of ' + lst[
                    8] + ' and has a MEM temperature of ' + lst[9] + '\n'
            text += '\n\n'

        message = 'Subject: {}\n\n{}'.format(SUBJECT, text)

        # Sending the Email
        if start_temp or start_cpu:
            smtp.sendmail("cpuutil@gmail.com", "harshit.19B101021@abes.ac.in", message)

        # Terminating the session
        smtp.quit()

    except Exception as ex:
        print("Something went wrong....", ex)


# update command
def update_command(line_counter, command_running, index):
    for ele in range(0, len(line_counter)):
        line_counter[ele] = 0
        command_running[ele] = False
    line_counter[index] += 1
    command_running[index] = True


# show process cpu
def show_process_cpu(index, cpu_taken, cpu_count, x):
    result = ''
    alert_ = '-1'
    if line_counter[index] == 1:
        result += sep_line
        result += 'show process cpu\n\n'
    line_counter[index] += 1
    a = re.search("%Cpu", x)
    b = re.search('MiB Mem :', x)
    c = re.search('PID', x)
    if a:
        result += x + '\n'
        cpulist = x.split()
        cpu_graph.append(float(cpulist[3]))
    if b:
        result += x + '\n'
    if c:
        cpu_taken = True
    if cpu_taken and cpu_count < 4:
        result += x + '\n'
        if cpu_count > 0:
            lst = x.split()
            cpu = lst[8]
            mem = lst[9]
            if float(cpu) >= 50 or float(mem) >= 50:
                alert_ = x
        cpu_count += 1
        if cpu_count == 4:
            result += '\n\n\n'
    return [result, cpu_taken, cpu_count, alert_]


# show version
def show_version(index, x):
    result = ''
    if line_counter[index] == 1:
        result += sep_line
        result += 'show version\n\n'
    line_counter[1] += 1
    a = re.search("SONiC Software Version:", x)
    b = re.search('Platform:', x)
    c = re.search('HwSKU: ', x)
    d = re.search("ASIC:", x)
    e = re.search('Serial Number:', x)
    f = re.search('Uptime:', x)
    if a:
        result += x + '\n'
    if b:
        result += x + '\n'
    if c:
        result += x + '\n'
    if d:
        result += x + '\n'
    if e:
        result += x + '\n'
    if f:
        result += x + '\n\n\n'
    return result


# show platform temperature
def show_platform_temperature(index, x):
    result = ''
    alert_ = '-1'
    add_or_not = '-1'
    if line_counter[index] == 1:
        result += sep_line
        result += 'show platform temperature\n\n'
    line_counter[index] += 1
    if line_counter[index] >= 5:
        add_or_not = x
    a = re.search('True', x)
    if line_counter[index] >= 3:
        result += x + '\n'
    if a:
        alert_ = x + '\n'
    return [result, alert_, add_or_not]


# show date
def show_date(index, x):
    result = ''
    date_and_time = '-1'
    if line_counter[index] == 1:
        result += sep_line
        result += 'date\n\n'
    line_counter[index] += 1
    a = re.search('UTC', x)
    if a:
        result += x + '\n\n\n'
        date_and_time = x
    return [result, date_and_time]


# show system memory
def show_system_memory(index, x):
    result = ''
    if line_counter[index] == 1:
        result += sep_line
        result += 'show system memory\n\n'

    line_counter[index] += 1
    a = re.search("total", x)
    b = re.search('Mem:', x)

    if a:
        result += x + '\n'
    if b:
        result += x + '\n\n\n'
    return result


# show docker stats
def show_docker_stats(index, x):
    result = ''
    add_or_not = '-1'
    if line_counter[index] == 1:
        result += sep_line
        result += 'show docker stats\n\n'
    line_counter[index] += 1
    if line_counter[index] >= 4:
        add_or_not = x
    if line_counter[index] >= 3:
        result += x + '\n'
    return [result, add_or_not]


# show processes memory
def show_processes_memory(index, process_taken, process_count, x):
    result = ''
    if line_counter[index] == 1:
        result += sep_line
        result += 'show processes memory\n\n'
    line_counter[index] += 1
    a = re.search("%Cpu", x)
    b = re.search('MiB Mem :', x)
    c = re.search('PID', x)

    if a:
        result += x + '\n'
    if b:
        result += x + '\n'
    if c:
        process_taken = True
    if process_taken and process_count < 4:
        result += x + '\n'
        process_count += 1
        if process_count == 4:
            result += '\n\n\n'
    return [result, process_taken, process_count]


# show interface counters
def show_interface_counters(counters_dict, index, x):
    result = ''
    a = re.search('U', x)
    b = re.search('D', x)
    if a or b:
        if line_counter[index] == 1:
            result += sep_line
            result += 'show interface counters\n\n'
        line_counter[index] += 1
        lst = x.split()
        counters_dict.append([lst[0], lst[1], lst[2], lst[8]])
        i = lst[0]
        j = [lst[1], lst[2], lst[8]]
        new_i = i
        for length in range(len(i), 15):
            new_i += ' '
        result += new_i
        for item in j:
            new_item = item
            for length in range(len(item), 15):
                new_item += ' '
            result += new_item
        result += '\n'
    return result


command = []
command.append('show processes cpu')
command.append('show version')
command.append('show platform temperature')
command.append('show system-memory')
command.append('show processes memory')
command.append('show interface counters')
command.append('date')
command.append('show processes summary')
command.append('docker stats  --no-stream')
ip_address = input("Enter the Ip address : ")
username = input("Enter the username : ")
password = input("Enter the password : ")
snapshot_count = int(input("Enter the snaphshot count you : "))
main(command, ip_address, username, password, snapshot_count)
