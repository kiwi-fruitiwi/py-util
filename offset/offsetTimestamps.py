import re


# shift all timestamps in a text file by a given offset in seconds
def applyTimestampOffsets(filePath, offsetSeconds, outputPath=None):
    # pattern to match timestamps in mm:ss format
    #   \b designates a word boundary
    #   \d{1,2} finds minutes, which is either one or two digits
    #   \d{2} looks for 2 seconds digits,
    #   finally, an ending \b to ensure a clean ending
    timestampPattern = re.compile(r'\b(\d{1,2}):(\d{2})\b')

    # find total number of seconds, subtract offset, then reform mm:ss format
    def adjustTimestamp(match):
        # convert matched hour and minutes strings to integers using map
        minutes, seconds = map(int, match.groups())
        totalSeconds = minutes * 60 + seconds + offsetSeconds

        # avoid negative time if total seconds is less than offset
        # this shouldn't ever happen though, so we'll assert
        assert totalSeconds >= 0

        newMinutes = totalSeconds // 60
        newSeconds = totalSeconds % 60

        # strip leading zero for newMinutes
        # this results in an empty string if we have zero minutes, so we use
        #   the (or '0') trick to put the '0' back
        return f"{str(newMinutes).lstrip('0') or '0'}:{newSeconds:02}"

    with open(filePath, 'r', encoding='utf-8') as inputFile:
        content = inputFile.read()

    # substitute all occurrences of timestamps with an offset timestamp
    adjustedContent = timestampPattern.sub(adjustTimestamp, content)

    # if output path is not specified, create a new file with suffix
    if not outputPath:
        outputPath = filePath.replace(".txt", "-adjusted.txt")

    with open(outputPath, 'w', encoding='utf-8') as outputFile:
        outputFile.write(adjustedContent)

    print(f"Updated file saved to: {outputPath}")


applyTimestampOffsets('input.txt', -18)