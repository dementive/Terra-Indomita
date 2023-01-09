li_five = [8433,8533,8435,8344,8636,8686,8488,8693,8553,8510,8477,8408,8344,8527,8997,9006,9651,9049]
li_ten = [8313,8504,8972,8446,8638,8742,8384,8379]
subjects = ["ZHO", "WZO", "EZO"]

def print_unification_scripts(li, num, subjects=[])
	# Print custom loc
	for i in li
		custom = "china_unify_#{i}_custom_loc = {
    type = country
    text = {
    	localization_key = CHINA_CUSTOM_OWNS_#{i}_LOC\n\t
    	trigger = {\t
    		owns_or_subject_owns = #{i}
    	}
    }
    text = {
    	localization_key = CHINA_CUSTOM_NOT_OWNS_#{i}_LOC\n\t
    	trigger = {\t
    		always = yes
    	}
    }
}\n";
		print custom
	end

	for i in subjects
		custom = "china_unify_#{i}_custom_loc = {
    type = country
    text = {
    	localization_key = CHINA_CUSTOM_SUBJECT_#{i}_LOC\n\t
    	trigger = {\t
    		c:#{i} = { is_subject_of = ROOT }
    	}
    }
    text = {
    	localization_key = CHINA_CUSTOM_NOT_SUBJECT_#{i}_LOC\n\t
    	trigger = {\t
    		always = yes
    	}
    }
}\n";
	print custom
	end

	print "\n--------------\n\n"

	# Print custom loc localization keys
	for i in li
		print("CHINA_CUSTOM_OWNS_#{i}_LOC:0 \"@trigger_yes! Owns or subject owns #Y [GetProvince('(int32)#{i}').GetName]#!\"\n")
		print("CHINA_CUSTOM_NOT_OWNS_#{i}_LOC:0 \"@trigger_no! Owns or subject owns #Y [GetProvince('(int32)#{i}').GetName]#!\"\n")
	end

	for i in subjects
		print "CHINA_CUSTOM_SUBJECT_#{i}_LOC:0 \"@trigger_yes! #Y [GetCountry('#{i}').GetName]#! is a subject of #Y [Player.GetName]#!.\"\n"
		print "CHINA_CUSTOM_NOT_SUBJECT_#{i}_LOC:0 \"@trigger_no! #Y [GetCountry('#{i}').GetName]#! is a subject of #Y [Player.GetName]#!.\"\n"
	end

	print "\n--------------\n"

	# Print tooltip for UI
	print "#{num}_POINT_PROVINCES_UNIFICATION_UI:0 \"Actions that give #{num} points:\\n\\n"
	for i in subjects
		print "[Player.Custom('china_unify_#{i}_custom_loc')]\\n"
	end
	for i in li
		print "[Player.Custom('china_unify_#{i}_custom_loc')]\\n"
	end
	print "\""
end

#print_unification_scripts(li_ten, "10")
print_unification_scripts(li_five, "5", subjects)