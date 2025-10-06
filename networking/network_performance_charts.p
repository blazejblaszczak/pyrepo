import threading
from scapy.all import ICMP, IP, sr1, sendp, Ether
import time
import statistics
import matplotlib.pyplot as plt


# global variables to hold measurement results
latency_results = []
packet_loss_count = 0
total_packets_sent = 0


# function to plot results
def plot_results():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle('Network Performance Metrics')
    ax1.plot(latency_results, marker='o')
    ax1.set_title('Latency Over Time')
    ax1.set_xlabel('Ping Attempt')
    ax1.set_ylabel('Latency (ms)')
    ax1.grid(True)
    # plot packet loss
    ax2.bar(['Packet Loss', 'Packets Received'], [packet_loss_count, len(latency_results)], color=['red', 'green'])
    ax2.set_title('Packet Loss')
    ax2.set_ylabel('Number of Packets')
    ax2.grid(True)
    if total_packets_sent > 0:
        bandwidth = total_packets_sent * 1000 * 8 / 5 / 1024 # kbps
        ax3.bar(['Estimated Bandwidth'], [bandwidth], color='blue')
        ax3.set_title('Estimated Bandwidth')
        ax3.set_ylabel('Bandwidth (Kbps)')
        ax3.grid(True)
    else:
        ax3.axis('off')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


def measure_latency(target_ip, count = 5):
    global latency_results
    for _ in range(count):
        start_time = time.time()
        reply = sr1(IP(dst=target_ip) / ICMP(), verbose=0, timeout=2)
        if reply:
            round_trip_time = (time.time() - start_time) * 1000 # convert to millisecond
            latency_results.append(round_trip_time)
        else:
            global packet_loss_count
            packet_loss_count += 1
        time.sleep(1) # wait for a second before the next ping


# to measure bandwidth by sending packets and measuring return rate
def measure_bandwidth(target_ip, size=1000, duration=5):
    start_time = time.time()
    packets_sent = 0
    while time.time() - start_time < duration:
        sendp(Ether() / IP(dst=target_ip) / ('X'*size), verbose=0)
        packets_sent += 1
        time.sleep(0.1) # send 10 packets per second
    global total_packets_sent
    total_packets_sent = packets_sent


def print_results():
    if latency_results:
        print(f"Average Latency: {statistics.mean(latency_results):.2f} ms")
        print(f"Minimum Latency: {min(latency_results):.2f} ms")
        print(f"Maximum Latency: {max(latency_results):.2f} ms")
    print(f"Packet Loss: {(packet_loss_count / (len(latency_results) + packet_loss_count) * 100):.2f}%")
    if total_packets_sent > 0:
        print(f"Estimated Bandwidth: {total_packets_sent * 1000 * 8 / 5 / 1024:.2f} Kbps")


def main(target_ip):
    threads = []
    threads.append(threading.Thread(target=measure_latency, args=(target_ip,)))
    threads.append(threading.Thread(target=measure_bandwidth, args=(target_ip,)))
    # start all threads
    for thread in threads:
        thread.start()
    # wait for all threads to complete
    for thread in threads:
        thread.join()
    print_results()
    plot_results()


if __name__ == "__main__":
    target_ip = "8.8.8.8"
    main(target_ip)
