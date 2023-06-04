# Localize culture names from error log entries

file = File.new("error.log", "r")

file.each do |line|
	re = line.match(/\[culture.cpp:641\]:(.*)/)
	if re
		puts re[1]
	end
end