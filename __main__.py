import os
import re
import json
import requests
import argparse


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    if iteration == total:
        print()


def fetch_messages(token, first_message, no_of_messages, channel_id, output_file=None):
    last_message_id = first_message
    timestamp = "0"

    req_limit = min(50, no_of_messages)
    remaining_messages = no_of_messages

    if output_file:
        f = open(output_file, "a+")
    else:
        f = None

    while remaining_messages > 0:
        limit = min(req_limit, remaining_messages)

        headers = {
            'authorization': token
        }
        r = requests.get(
            f'https://discord.com/api/v9/channels/{channel_id}/messages?before={last_message_id}&limit={limit}', headers=headers)
        data = json.loads(r.text)

        if not data:
            break

        for value in data:
            msg = value["author"]["username"] + ":" + value["content"]
            formatted = re.sub(r'<:(.*?):\d+>|(\n)', lambda x: ':' +
                               (x.group(1) if x.group(1) else '§') + ':', msg) + '\n'
            if f:
                f.write(formatted)
            else:
                print(formatted)

            last_message_id = value["id"]
            timestamp = value["timestamp"]
            remaining_messages -= 1

        print_progress_bar(no_of_messages - remaining_messages,
                           no_of_messages, prefix="Fetching messages")

    if f:
        f.close()

    timestamp = re.sub(
        r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):\d{2}\.\d{6}\+\d{2}:\d{2}", r"\1-\2-\3:\4-\5", timestamp)
    print(f"\nTimestamp: {timestamp}")

    return last_message_id


def main():
    parser = argparse.ArgumentParser(description='Discord Messages Archiver')
    parser.add_argument('--token', help='Discord Bot Token', required=True)
    parser.add_argument('--first-message-id',
                        help='ID of the first message (latest)', required=True)
    parser.add_argument('--no-of-messages', type=int,
                        help='Number of messages to fetch', required=True)
    parser.add_argument(
        '--channel-id', help='Discord Channel ID', required=True)
    parser.add_argument('--output-file', help='File to append the output to')

    args = parser.parse_args()

    last_message_id = fetch_messages(args.token, args.first_message_id,
                                     args.no_of_messages, args.channel_id, args.output_file)

    output_summary = f"Messages backed up: {args.no_of_messages}"
    if args.output_file:
        output_summary += f"\nOutput file: {args.output_file}"
    output_summary += f"\nLast message ID read: {last_message_id}"

    print(output_summary)


if __name__ == "__main__":
    main()
