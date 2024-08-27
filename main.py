# Import necessary modules
from machine import Pin, Timer
import time
import bluetooth
from ic_translate import *
from ic_io import get_device_data, save_device_data
from ble_uart_peripheral import BLEUART


def is_float(element: any) -> bool:
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


print(device_boot_text)

# Create a Pin object for the onboard LED, configure it as an output
led = Pin("LED", Pin.OUT)
led.value(0)

relay_enable_pin = Pin(0, Pin.OUT)
relay_enable_pin.value(0)

json_save_data = get_device_data()

ble = bluetooth.BLE()
uart = BLEUART(ble)

delay_operation_running = False
press_on_power_button_timer = Timer(-1)


def set_delay_operation_running(enabled: bool):
    global delay_operation_running
    delay_operation_running = enabled


def on_rx():
    try:
        if delay_operation_running:
            return
        decoded_text = uart.read().decode().strip()
        if decoded_text == "":
            return
        parts_list = [part for part in decoded_text.split(device_split_arg)]
        if len(parts_list) == 0:
            return
        if parts_list[0] == help_command_name:
            uart.write(help_text)
            print(device_performed_Command.format(help_command_name))
            return
        if len(parts_list) >= 3 and parts_list[0] == pw_command_name and parts_list[2] == json_save_data[
            device_io_pw_name]:
            if parts_list[1] != "":
                json_save_data[device_io_pw_name] = parts_list[1]
                save_device_data(json_save_data)
                uart.write(is_valid_pw_command_text)
            else:
                uart.write(is_no_valid_pw_command_text)
        if len(parts_list) >= 3 and parts_list[0] == name_command_name and parts_list[2] == json_save_data[
            device_io_pw_name]:
            if parts_list[1] != "":
                json_save_data[device_io_device_name] = parts_list[1]
                save_device_data(json_save_data)
                uart.write(is_valid_name_command_text)
            else:
                uart.write(is_no_valid_name_command_text)
        if len(parts_list) >= 3 and parts_list[0] == on_command_name and parts_list[2] == json_save_data[
            device_io_pw_name]:
            if is_float(parts_list[1]):
                seconds = float(parts_list[1])
                if seconds <= 0:
                    seconds = 0.5
                if seconds >= 5:
                    seconds = 5
                set_delay_operation_running(True)
                uart.write(is_valid_on_command_text.format(seconds))
                led.value(1)
                # Enable Relay ->
                relay_enable_pin.value(1)
                ms = int(seconds * 1000)

                def finsh_power_btn_press():
                    led.value(0)
                    # Disable Relay ->
                    relay_enable_pin.value(0)
                    uart.write(is_success_on_command_text)
                    print(device_performed_Command.format(on_command_name))
                    set_delay_operation_running(False)

                press_on_power_button_timer.init(period=ms, mode=Timer.ONE_SHOT, callback=lambda t: finsh_power_btn_press())
            else:
                uart.write(is_no_valid_seconds_on_command_text)
    except KeyboardInterrupt:
        pass


uart.irq(handler=on_rx)

welcomed = False
welcome_timer = Timer(-1)

operation_reset = False
operation_reset_timer = Timer(-1)


def set_operation_running(enabled: bool):
    global operation_reset
    operation_reset = enabled


try:
    while True:
        if uart.is_connected():
            if not welcomed:
                welcomed = True
                print(device_connected_Command)
                welcome_timer.init(period=2000, mode=Timer.ONE_SHOT, callback=lambda t: uart.write(welcome_text))
        else:
            if welcomed:
                print(device_disconnected_Command)
                welcomed = False

        if delay_operation_running:
            if not operation_reset:
                set_operation_running(True)


                def reset_operation():
                    if delay_operation_running:
                        set_delay_operation_running(False)
                        set_operation_running(False)


                operation_reset_timer.init(period=6000, mode=Timer.ONE_SHOT, callback=lambda t: reset_operation())
        else:
            set_operation_running(False)

        time.sleep_ms(500)
except KeyboardInterrupt:
    pass

uart.close()
