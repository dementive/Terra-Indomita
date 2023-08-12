# Localize unrecognized loc keys from error log

file = File.new("error.log", "r")

file.each do |line|
	re = line.match(/\[jomini_dynamicdescription.cpp:66\]: Unrecognized loc key (.*\s\s)/)
	if re
		puts "#{re[1].delete_suffix(".\s\s")}:0 \"\""
	end
end
