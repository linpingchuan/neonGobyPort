#!/usr/bin/env python

# Author: Jingyue
# May be slow on large programs

import re, os, sys
import argparse

class NodeInfo:
    def __init__(self, node_id, label, is_top_level):
        self.node_id = node_id
        self.label = label
        self.is_top_level = is_top_level

global nodes
global edges

def process_line(line, mode):
    what = re.match("(\\w+), (\\d+) => (\\w+), (\\d+)", line)
    if what != None:
        addr_1 = what.group(1)
        ver_1 = what.group(2)
        addr_2 = what.group(3)
        ver_2 = what.group(4)
        process_addr_taken(addr_1, ver_1, addr_2, ver_2, mode)
        return

    what = re.match("(\\d+), (\\d+) => (\\w+), (\\d+)", line)
    if what != None:
        vid_1 = what.group(1)
        ver_1 = what.group(2)
        addr_2 = what.group(3)
        ver_2 = what.group(4)
        process_top_level(vid_1, ver_1, addr_2, ver_2, mode)
        return

    what = re.match("(\\w+), (\\d+), (\\d+)", line)
    if what != None:
        addr = what.group(1)
        ver = what.group(2)
        vid = what.group(3)
        declare_addr_taken(addr, ver, vid, mode)
        return

    print >> sys.stderr, line
    assert False

def declare_addr_taken(addr, ver, vid, mode):
    if mode == "static":
        add_node(vid, vid, False)
    else:
        add_node((addr, ver), vid + ":" + ver, False)

def process_addr_taken(addr_1, ver_1, vid_1, addr_2, ver_2, vid_2, mode):
    if mode == "static":
        add_edge(vid_1, vid_1, vid_2, vid_2, False)
    else:
        add_edge((addr_1, ver_1), vid_1 + ":" + ver_1,
                (addr_2, ver_2), vid_2 + ":" + ver_2, False)

def process_top_level(vid_1, ver_1, addr_2, ver_2, vid_2, mode):
    if mode == "static":
        add_edge(vid_1, vid_1, vid_2, vid_2, True)
    else:
        add_edge((vid_1, ver_1), vid_1 + ":" + ver_1,
                (addr_2, ver_2), vid_2 + ":" + ver_2, True)


def add_node(key, label, is_top_level):
    if key not in nodes:
        node_id = len(nodes)
        nodes[key] = NodeInfo(node_id, label, is_top_level)
    else:
        node_id = nodes[key].node_id
    return node_id

# is_top_level: whether the first node corresponds to a top-level variable. 
def add_edge(key_1, label_1, key_2, label_2, is_top_level):
    node_id_1 = add_node(key_1, label_1, is_top_level)
    # The pointee is always an addr-taken variable. 
    node_id_2 = add_node(key_2, label_2, False)
    edges.append((node_id_1, node_id_2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description = "Generate a static or dynamic point-to graph");
    parser.add_argument("--mode",
            help = "static or dynamic",
            choices = ["static", "dynamic"],
            required = True)
    args = parser.parse_args()

    nodes = {}
    edges = []
    for line in sys.stdin:
        process_line(line, args.mode)

    sys.stdout.write("strict digraph point_to {\n")
    for node_info in nodes.values():
        sys.stdout.write("node" + str(node_info.node_id) + " ")
        sys.stdout.write("[label = \"" + node_info.label + "\"")
        if node_info.is_top_level:
            sys.stdout.write(", shape = box")
        sys.stdout.write("]\n")
    for edge in edges:
        sys.stdout.write("node" + str(edge[0]) + " -> ")
        sys.stdout.write("node" + str(edge[1]) + "\n")
    sys.stdout.write("}\n")