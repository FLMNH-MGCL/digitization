using ArgParse
using Pandas

# THIS FILE IS NOT INTENDED FOR USE! 
# I am trying to learn Julia by converting my latest script.

# there are no classes in Julia... so this will be interesting

function parse_commandline()
    s = ArgParseSettings()

    add_arg_group!(s, "Mutually exclusive options", exclusive = true, required = true)
    @add_arg_table! s begin
        "--range", "-r"
        nargs = 2
        help = "The lower and upper bound MGCL numbers, from LOWER to UPPER (inclusive)"
        metavar = ["LOWER", "UPPER"]

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

function main()
    parsed_args = parse_commandline()
    println("Parsed args:")
    for (arg, val) in parsed_args
        println("  $arg  =>  $val")
    end
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