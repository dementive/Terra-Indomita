# Localize gui icon names

file = File.new("cde_mission_images_icons.gui", "r")

file.each do |line|
	re = line.match(/icon\s?=\s?([A-Za-z_]*)$/)
	if re
		puts "#{re[1]}:0 \"@#{re[1]}!\""
	end
end