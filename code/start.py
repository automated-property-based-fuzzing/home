import argparse
from main import NonCrashDetector 

def parse_args():
    """
    parse command line input
    """
    parser = argparse.ArgumentParser(description="Start NonCrashDetector to detect non-crash bugs.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-device_serial', action='store', dest="device_serial", required=False, default="emulator-5554",
                        help="Serial of the device")
    parser.add_argument("-root_path", action="store", dest="root_path", required=False, default="../output/",
                        help="The path to store the output file")
    parser.add_argument("-app_path", action="store", dest="app_path", required=True,
                        help="The path of the app you want to test")
    parser.add_argument("-policy_name", action="store", dest="policy_name", required=False, default="random",
                        help="Policy name")
    parser.add_argument("-choice", action="store", dest="choice", required=False, default="0",
                        help="")
    parser.add_argument("-testcase_count", action="store", dest="testcase_count", required=False, default=10, type=int,
                        help="How many testcases are generated for each strategy")
    parser.add_argument("-start_testcase", action="store", dest="start_testcase", required=False, default=0, type=int,
                        help="The start testcase num")
    parser.add_argument("-event_num", action="store", dest="event_num", required=False, default=1000, type=int,
                        help="How many events are in each test case")
    parser.add_argument("-max_time", action="store", dest="max_time", required=False, default=57600, type=int,
                        help="Max time")
    parser.add_argument("-json_name", action="store", dest="json_name", required=False, default="",
                        help="The name of json file")
    parser.add_argument("-testcase_path", action="store", dest="testcase_path", required=False, default="../testcase/",
                        help="The path to store the testcase file")
    parser.add_argument("-result_path", action="store", dest="result_path", required=False, default="",
                        help="The path to store the result")
    parser.add_argument("-input_path", action="store", dest="input_path", required=False, default="",
                        help="The path of the input")
    parser.add_argument("-input_file_name", action="store", dest="input_file_name", required=False, default="all_trace.txt",
                        help="The name of the input file")
    parser.add_argument("-target_hash", action="store", dest="target_hash", required=False, default="",
                        help="target hash of dmf")
    parser.add_argument("-clear_and_start_flag", action="store", dest="clear_and_start_flag", required=False, default="True",
                        help="clear and restart flag")

    options = parser.parse_args()
    # print options
    return options

def main():
    opts = parse_args()
    import os
    if not os.path.exists(opts.app_path):
        print("APK does not exist.")
        return

    nltester = NonCrashDetector(
        device_serial=opts.device_serial,
        root_path=opts.root_path,
        app_path=opts.app_path,
        choice = opts.choice,
        policy_name = opts.policy_name,
        testcase_count = opts.testcase_count,
        event_num = opts.event_num,
        json_name = opts.json_name,
        testcase_path = opts.testcase_path,
        result_path = opts.result_path,
        max_time = opts.max_time,
        start_testcase = opts.start_testcase,
        clear_and_start_flag = opts.clear_and_start_flag,
        input_path=opts.input_path,
        input_file_name=opts.input_file_name,
        target_hash = opts.target_hash.split(',')
    )
    nltester.start()
    nltester.stop()

if __name__ == "__main__":
    main()