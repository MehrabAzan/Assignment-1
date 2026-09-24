import heapq
import sys
from collections import Counter

def count_frequencies(text):
    """
    Count how often each character appears in text.
    Input: text (str).
    Output: dict symbol -> positive int frequency.
    Locals: freqMap.
    """
    freqMap = dict(Counter(text))
    return freqMap

def build_huffman_tree(freqMap):
    """
    Build a Huffman tree using a binary min-heap priority queue.
    Each heap entry is (weight, tieId, symbolOrNone, left, right).
    Leaves store the symbol; internal nodes store None.
    Input: freqMap (symbol -> positive frequency).
    Output: root heap-entry tuple, or None if freqMap is empty.
    Locals: heapList, tieId, symbol, weight, leftNode, rightNode, parentNode.
    """
    if not freqMap:
        return None

    heapList = []
    tieId = 0
    for symbol, weight in freqMap.items():
        heapq.heappush(heapList, (weight, tieId, symbol, None, None))
        tieId += 1

    if len(heapList) == 1:
        return heapList[0]

    while len(heapList) > 1:
        leftNode = heapq.heappop(heapList)
        rightNode = heapq.heappop(heapList)
        parentNode = (
            leftNode[0] + rightNode[0],
            tieId,
            None,
            leftNode,
            rightNode,
        )
        tieId += 1
        heapq.heappush(heapList, parentNode)

    return heapList[0]

def assign_codes(rootNode):
    """
    Walk the Huffman tree and assign a bit string to each leaf symbol.
    Input: rootNode from build_huffman_tree (or None).
    Output: dict symbol -> code string (bits as '0'/'1').
    Locals: codeMap, stack, node, prefix, weight, tieId, symbol, leftNode, rightNode.
    """
    codeMap = {}
    if rootNode is None:
        return codeMap

    weight, tieId, symbol, leftNode, rightNode = rootNode
    if leftNode is None and rightNode is None:
        codeMap[symbol] = "0"
        return codeMap

    stack = [(rootNode, "")]
    while stack:
        node, prefix = stack.pop()
        weight, tieId, symbol, leftNode, rightNode = node
        if leftNode is None and rightNode is None:
            codeMap[symbol] = prefix
            continue
        if rightNode is not None:
            stack.append((rightNode, prefix + "1"))
        if leftNode is not None:
            stack.append((leftNode, prefix + "0"))
    return codeMap

def encode_text(text, codeMap):
    """
    Encode text with the given Huffman codes.
    Input: text, codeMap (symbol -> bit string).
    Output: bit string for the whole text.
    Locals: bitParts, ch.
    """
    bitParts = []
    for ch in text:
        bitParts.append(codeMap[ch])
    return "".join(bitParts)

def decode_bits(bitString, rootNode):
    """
    Decode a Huffman bit string by walking the tree from the root.
    Input: bitString, rootNode.
    Output: decoded text string.
    Locals: outChars, node, bit, weight, tieId, symbol, leftNode, rightNode.
    """
    if rootNode is None:
        return ""

    weight, tieId, symbol, leftNode, rightNode = rootNode
    if leftNode is None and rightNode is None:
        return symbol * len(bitString)

    outChars = []
    node = rootNode
    for bit in bitString:
        weight, tieId, symbol, leftNode, rightNode = node
        if bit == "0":
            node = leftNode
        else:
            node = rightNode
        weight, tieId, symbol, leftNode, rightNode = node
        if leftNode is None and rightNode is None:
            outChars.append(symbol)
            node = rootNode
    return "".join(outChars)

def average_code_length(freqMap, codeMap):
    """
    Expected / average code length under the empirical distribution.
    Input: freqMap, codeMap.
    Output: float average bits per symbol.
    Locals: totalCount, weightedSum, symbol, weight.
    """
    totalCount = sum(freqMap.values())
    if totalCount == 0:
        return 0.0
    weightedSum = 0
    for symbol, weight in freqMap.items():
        weightedSum += weight * len(codeMap[symbol])
    return weightedSum / totalCount

def print_frequency_table(freqMap):
    """
    Print symbols and frequencies sorted by symbol.
    Input: freqMap.
    Output: none (prints a table).
    Locals: symbol, weight, totalCount.
    """
    totalCount = sum(freqMap.values())
    print("Frequencies (symbol -> count):")
    for symbol in sorted(freqMap.keys(), key=lambda s: (len(s), s)):
        weight = freqMap[symbol]
        print(f"  {repr(symbol):>6} : {weight}")
    print(f"  total symbols in text: {totalCount}")
    print(f"  distinct code symbols n: {len(freqMap)}")

def print_code_table(codeMap, freqMap):
    """
    Print Huffman codes with frequencies.
    Input: codeMap, freqMap.
    Output: none (prints a table).
    Locals: symbol, codeBits.
    """
    print("Huffman codes (symbol -> bits):")
    for symbol in sorted(codeMap.keys(), key=lambda s: (len(codeMap[s]), s)):
        codeBits = codeMap[symbol]
        print(f"  {repr(symbol):>6} : {codeBits}  (freq {freqMap[symbol]})")

def run_huffman(text):
    """
    Build Huffman codes for text, encode, decode, and print a report.
    Input: text (non-empty str).
    Output: True if round-trip succeeds, False otherwise.
    Locals: freqMap, rootNode, codeMap, bitString, decodedText, avgLen, ok.
    """
    freqMap = count_frequencies(text)
    print_frequency_table(freqMap)
    print()

    rootNode = build_huffman_tree(freqMap)
    codeMap = assign_codes(rootNode)
    print_code_table(codeMap, freqMap)
    print()

    avgLen = average_code_length(freqMap, codeMap)
    print(f"average / expected code length: {avgLen:.6f} bits/symbol")

    bitString = encode_text(text, codeMap)
    print(f"encoded bit length: {len(bitString)} bits")
    print(f"encoded bits: {bitString}")

    decodedText = decode_bits(bitString, rootNode)
    ok = decodedText == text
    print(f"decoded text: {repr(decodedText)}")
    print(f"round-trip ok: {ok}")
    return ok

def read_cli_text(argvList):
    """
    Resolve input text from CLI args or the built-in demo sample.
    Input: argvList (sys.argv without the script name).
    Output: (text, sourceLabel) where sourceLabel describes where text came from.
    Locals: joinedArgs, demoText.
    """
    if argvList:
        joinedArgs = " ".join(argvList)
        return joinedArgs, "command-line arguments"
    demoText = "this is an example of a huffman tree"
    return demoText, "built-in demo sample"

def main():
    """
    Run Huffman coding on CLI text or a demo sample; echo the input.
    Input: optional text on the command line (remaining argv joined by spaces).
    Output: frequencies, codes, encoding, decode check; exit status via return.
    Locals: text, sourceLabel, ok.
    """
    text, sourceLabel = read_cli_text(sys.argv[1:])
    print(f"read input source: {sourceLabel}")
    print(f"read text: {repr(text)}")
    print()

    if text == "":
        print("error: empty text; need at least one character")
        return 1

    ok = run_huffman(text)
    if not ok:
        print("error: encode/decode round-trip failed")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())