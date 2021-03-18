using ArgParse
using CSV
using DataFrames
using Logging

# THIS FILE IS NOT INTENDED FOR USE! 
# I am trying to learn Julia by converting my latest script.

# there are no classes in Julia... so this will be interesting


# TODO: figure me out plz
# io = open("log.txt", "w+")
# logger = SimpleLogger(io)

# this is all for the most part the same as I would define my CLI args in python.
# I don't particularly love the syntax for the arg tables, but it isn't that bad.
function parse_commandline()
    s = ArgParseSettings()

    add_arg_group!(s, "Mutually exclusive options", exclusive = true, required = true)
    @add_arg_table! s begin
        "--range", "-r"
        nargs = 2
        help = "The lower and upper bound MGCL numbers, from LOWER to UPPER (inclusive)"
        metavar = ["LOWER", "UPPER"]
        arg_type = Int

        "--file", "-f"
        help = "A CSV/XLSX of MGCL Numbers to search for"
    end

    add_arg_group!(s, "Required arguments", required = true)
    @add_arg_table s begin
        "--start_dir", "-d"
        help = "path to the starting directory"
        required = true

        "--exts", "-e"
        help = "The upper bound MGCL number to include in count (default is png jpg jpeg)"
        default = ["png", "jpg", "jpeg"]
        required = false
    end

    return parse_args(s)
end


function extract_number(filename)
    pattern = r"(?:MGCL_)(\d*)(?:.*)"

    numbers = map(eachmatch(pattern, filename)) do m
        parse(Int, m[1])
    end

    if length(numbers) > 1
        # handle me
    end

    # oh no.... this took me an hour to figure out that Julia is 
    # indexed starting at ONE :( By far my least favorite Data Science
    # thing. The errors Julia produces are kinda eh to be honest.
    # See rust for amazing error output, sometimes I swear rust has
    # ai in their compiler.
    return numbers[1]
end


function parse_file(_file)
    # normally I would not do this in three separate patterns,
    # however I could not find a concise way of extracting the suffix of a
    # file _safely_. I python I just use Path objects.
    csv_pattern = r".*\.csv$"
    xlsx_pattern = r".*\.xlsx$"
    both_pattern = r".*(?:\.csv$|\.xlsx$)"

    # null would have been quicker to type lol
    raw_data = nothing

    # so naturally if you are going to have an isnothing in your std lib then
    # issomething should also be there. It's not a big deal, I'm just being 
    # a brat.
    if isnothing(match(both_pattern, _file))
        # TODO throw and error

    elseif isnothing(match(csv_pattern, _file))
        # handle me
        # raw_data = read_excel(_file)
    else
        # in python I would use pandas for almost everything and everthing like this,
        # however the Pandas package for Julia is actually a wrapper around the package.
        # So to try and separate this file I decided not to use it.
        raw_data = DataFrame(CSV.File(_file, header = 1))
    end

    accounted_for = Dict{Int,Bool}()

    for r in eachrow(raw_data)
        accounted_for[extract_number(r.catalogNumber)] = false
    end

    return accounted_for
end


function parse_range(range)
    lower = range[1]
    upper = range[2]

    if upper < lower
        # TODO throw an error
    end

    accounted_for = Dict{Int,Bool}()

    for i = lower:upper
        accounted_for[i] = false
    end

    return accounted_for
end


function walk(accounted_for, start_dir, exts, range)
    ext_string = join(exts, "|")
    pattern = Regex(".*($ext_string)\$")



    print("Starting os walk...")

    # TODO: this needs error handling
    for (root, dirs, files) in walkdir(start_dir)
        for file in files
            if !isnothing(match(pattern, file))
                num = extract_number(file)

                if !isnothing(range)
                    lower = range[1]
                    upper = range[2]

                    if num < lower || num > upper
                        # TODO handle me
                        @debug "Number $num in $file is out of range"
                    elseif !haskey(accounted_for, num)
                        # TODO unexpected error, this should not happen
                        @warn "Number $num in $file is in range but was somehow excluded (is it an integer?)"
                    elseif accounted_for[num] == false
                        accounted_for[num] = true
                        @debug "Found number $num in $file"
                    end

                elseif haskey(accounted_for, num) && accounted_for[num] == false
                    accounted_for[num] = true
                    @debug "Found number $num in $file"
                end
            end

        end
    end

    println(" done!")

    return accounted_for

end

function main()
    parsed_args = parse_commandline()

    exts = parsed_args["exts"]
    range = parsed_args["range"]
    start_dir = parsed_args["start_dir"]
    _file = parsed_args["file"]

    accounted_for = nothing

    if !isnothing(_file)
        accounted_for = parse_file(_file)

    else
        accounted_for = parse_range(range)
    end

    updated = walk(accounted_for, start_dir, exts, range)

    finds = filter(entry -> entry.second == true, updated)

    print(finds)
end

main()

# Notes
#
# I'm making this to learn the language, I'll make some notes and comments both 
# throughout the code and down below.
#
####################################################################################
#
# Dictionaries! -> https://docs.julialang.org/en/v1/base/collections/#Dictionaries
#
# Basically the same as python. Curly bracket initialization has been deprecated,
# so instantiation is along the lines of:
#
# myDict = Dict() --> creates Dict{Any,Any}()
# myDict["firstkey"] = "firstvalue" --> creates Dict{Any,Any} with 1 entry: "firstkey" => "firstvalue"
#
# You can check existance of keys AND key-value pairs which is cool:
#
# haskey(myDict, "Z") --> false
# in(("firstkey" => "firstvalue"), myDict) --> true
#
# see more --> https://en.wikibooks.org/wiki/Introducing_Julia/Dictionaries_and_sets
#
####################################################################################
#
# TODO more notes
#
####################################################################################


# https://discourse.julialang.org/t/why-is-os-walk-regex-so-much-slower-than-glob/43906
#
# Apparently there were issues with Julias os walk implementation (see above link). I'll 
# be sure to create two variants to test whether or not the issues were actually fixed.
#
##########################################
#
# OPTION 1 - glob (had no issues)
#
# files = glob("MATCH_GLOB", ".")
# for file in files 
#     if occursin("MisleadingDirectoryName", file)  && continue
#     #do input
#     end
# end
#
##########################################
#
# OPTION 2 - walkdir (had issues)
#
# for (root, dirs, files) in walkdir(".")
#     #This is how I handled not going into directories with false information that I didn't want to parse later
#      deleteat!(dirs,findall(x->"MisleadingDirectoryName",dirs))
#      for file in files
#            if match(MATCH_REGEX, file).match
#                 #do input
#            end
#       end
# end
#
##########################################